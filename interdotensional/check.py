"""Validate that every theme/font combination renders cleanly.

This is the safety net for maintaining many themes: a token typo or a
missing tool section in one theme config surfaces here instead of as a
silently broken config file weeks later.
"""

from dataclasses import dataclass, field

from .config import (
    ConfigError,
    Project,
    available_colorschemes,
    available_fonts,
    available_themes,
    load_context,
)
from .generate import try_render_all
from .preview import _parse_hex
from .tokens import flatten_dict


@dataclass
class CheckReport:
    theme: str
    font: str
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def check_combination(project: Project, theme: str, font: str) -> CheckReport:
    """Render every template for one theme/font pair, collecting all problems."""
    report = CheckReport(theme=theme, font=font)
    try:
        context = load_context(project, theme=theme, font=font)
    except ConfigError as exc:
        report.errors.append(str(exc))
        return report
    for path, token in context.unresolved:
        report.errors.append(f"unresolved token {token} at {path}")
    _, errors = try_render_all(project, context)
    report.errors.extend(errors)
    return report


def check_matrix(
    project: Project,
    themes: list[str] | None = None,
    fonts: list[str] | None = None,
) -> list[CheckReport]:
    themes = themes if themes is not None else available_themes(project)
    fonts = fonts if fonts is not None else available_fonts(project)
    return [
        check_combination(project, theme, font)
        for theme in themes
        for font in fonts
    ]


def check_project_warnings(project: Project) -> list[str]:
    """Cross-cutting hygiene warnings that are not tied to one theme/font pair."""
    from .config import load_colorscheme, load_yaml

    warnings = []
    themes = set(available_themes(project))
    schemes = set(available_colorschemes(project))
    used_schemes = set()
    for name in sorted(themes):
        config = load_yaml(project.themes_dir / f"{name}.yml")
        wanted = config.get("colorscheme", name) if isinstance(config, dict) else name
        used_schemes.add(wanted)
        if wanted not in schemes:
            warnings.append(f"theme {name!r} needs colorscheme {wanted!r}, which does not exist")
    for name in sorted(schemes - used_schemes):
        warnings.append(f"colorscheme {name!r} is not used by any theme")
    for name in sorted(schemes):
        try:
            palette = flatten_dict(load_colorscheme(project, name))
        except ConfigError as exc:
            warnings.append(str(exc))
            continue
        for token, value in palette.items():
            if _parse_hex(value) is None:
                warnings.append(
                    f"colorscheme {name!r}: token {token!r} is not a hex color ({value!r})"
                )
    return warnings
