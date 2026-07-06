"""Symlink deployment: point dotfile locations at generated output files.

Configured in ``config/general.yml``::

    links:
      ~/.config/kitty/kitty.conf: kitty/kitty.conf
      ~/.tmux.conf: tmux/.tmux.conf

Keys are the destinations in your home directory; values are paths relative
to ``output/``.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from .config import ConfigError, Project


@dataclass
class LinkResult:
    target: Path  # the symlink location (e.g. ~/.tmux.conf)
    source: Path  # the file it should point to (under output/)
    # "ok" | "created" | "retargeted" | "conflict" | "missing-source"
    status: str
    detail: str = ""


def plan_links(project: Project, links: dict) -> list[LinkResult]:
    """Inspect each configured link and decide what needs to happen."""
    if not isinstance(links, dict):
        raise ConfigError("`links:` in general.yml must be a mapping of target: output-path.")
    results = []
    for raw_target, raw_source in links.items():
        target = Path(os.path.expandvars(str(raw_target))).expanduser()
        source = (project.output_dir / str(raw_source)).resolve()
        if not source.exists():
            results.append(
                LinkResult(target, source, "missing-source",
                           "generate first, or fix the output path")
            )
        elif target.is_symlink():
            if target.resolve() == source:
                results.append(LinkResult(target, source, "ok"))
            else:
                results.append(
                    LinkResult(target, source, "retargeted",
                               f"currently points to {os.readlink(target)}")
                )
        elif target.exists():
            results.append(
                LinkResult(target, source, "conflict",
                           "a real file exists here; use --force to back it up and replace")
            )
        else:
            results.append(LinkResult(target, source, "created"))
    return results


def apply_links(results: list[LinkResult], force: bool = False) -> None:
    """Create/fix the symlinks planned by :func:`plan_links` (mutates statuses)."""
    for result in results:
        if result.status in ("ok", "missing-source"):
            continue
        if result.status == "conflict":
            if not force:
                continue
            backup = result.target.with_name(result.target.name + ".bak")
            os.replace(result.target, backup)
            result.detail = f"existing file backed up to {backup}"
        elif result.status == "retargeted":
            result.target.unlink()
        result.target.parent.mkdir(parents=True, exist_ok=True)
        result.target.symlink_to(result.source)
        if result.status == "conflict":
            result.status = "created"
