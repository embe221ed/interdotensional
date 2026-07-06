"""Template discovery, rendering, and output writing."""

import difflib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError

from .config import Context, Project


class GenerationError(Exception):
    """A template failed to render."""


@dataclass
class RenderResult:
    template: str  # e.g. "kitty/kitty.conf.j2"
    rel_output: str  # e.g. "kitty/kitty.conf"
    content: str
    # "created" | "updated" | "unchanged"; set once compared against disk
    status: str = ""

    def output_path(self, project: Project) -> Path:
        return project.output_dir / self.rel_output


def discover_templates(project: Project) -> list[str]:
    """Every ``templates/<tool>/<name>.j2`` renders to ``output/<tool>/<name>``."""
    if not project.templates_dir.is_dir():
        raise GenerationError(f"Templates directory not found: {project.templates_dir}")
    return sorted(
        str(p.relative_to(project.templates_dir))
        for p in project.templates_dir.rglob("*.j2")
    )


def build_environment(project: Project) -> Environment:
    env = Environment(
        loader=FileSystemLoader(searchpath=str(project.templates_dir)),
        undefined=StrictUndefined,
    )
    from .filters import FILTERS

    env.filters.update(FILTERS)
    return env


def render_all(project: Project, context: Context) -> list[RenderResult]:
    """Render every discovered template. Raises GenerationError on the first failure,
    naming the template so the user knows which theme/template pair to fix."""
    results, errors = try_render_all(project, context)
    if errors:
        raise GenerationError(errors[0])
    return results


def try_render_all(
    project: Project, context: Context
) -> tuple[list[RenderResult], list[str]]:
    """Like :func:`render_all`, but keeps going after failures and returns
    every error - so ``check`` can report all broken templates at once."""
    env = build_environment(project)
    results, errors = [], []
    for template_name in discover_templates(project):
        try:
            template = env.get_template(template_name)
            content = template.render(**context.data)
        except TemplateError as exc:
            errors.append(
                f"failed to render {template_name} "
                f"(theme={context.theme_name}, font={context.font_name}): {exc}"
            )
            continue
        results.append(
            RenderResult(
                template=template_name,
                rel_output=str(Path(template_name).with_suffix("")),
                content=content,
            )
        )
    return results, errors


def compare_with_disk(project: Project, results: list[RenderResult]) -> None:
    """Set each result's status by comparing rendered content with the existing file."""
    for result in results:
        path = result.output_path(project)
        if not path.exists():
            result.status = "created"
            continue
        try:
            existing = path.read_text()
        except (OSError, UnicodeDecodeError):
            result.status = "updated"
            continue
        result.status = "unchanged" if existing == result.content else "updated"


def write_results(project: Project, results: list[RenderResult]) -> None:
    """Write changed outputs atomically (temp file + rename); skip unchanged ones."""
    for result in results:
        if result.status == "unchanged":
            continue
        path = result.output_path(project)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w") as f:
                f.write(result.content)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


def diff_results(project: Project, results: list[RenderResult]) -> str:
    """Unified diff between what is on disk and what would be written."""
    chunks = []
    for result in results:
        if result.status == "unchanged":
            continue
        path = result.output_path(project)
        try:
            existing = path.read_text().splitlines(keepends=True) if path.exists() else []
        except (OSError, UnicodeDecodeError):
            # Matches compare_with_disk: an unreadable existing file is treated
            # as "no prior content" so --diff shows the full new file instead
            # of crashing.
            existing = []
        diff = difflib.unified_diff(
            existing,
            result.content.splitlines(keepends=True),
            fromfile=f"a/output/{result.rel_output}",
            tofile=f"b/output/{result.rel_output}",
        )
        chunks.append("".join(diff))
    return "\n".join(chunk for chunk in chunks if chunk)
