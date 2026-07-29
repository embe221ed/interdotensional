"""Project layout and configuration loading."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .tokens import find_unresolved_tokens, flatten_dict, substitute_tokens


class ConfigError(Exception):
    """A configuration problem the user can fix (bad selection, missing file, invalid YAML)."""


@dataclass(frozen=True)
class Project:
    """Filesystem layout of an interdotensional checkout."""

    root: Path

    @property
    def config_dir(self) -> Path:
        return self.root / "config"

    @property
    def general_path(self) -> Path:
        return self.config_dir / "general.yml"

    @property
    def themes_dir(self) -> Path:
        return self.config_dir / "themes"

    @property
    def fonts_dir(self) -> Path:
        return self.config_dir / "fonts"

    @property
    def colorschemes_dir(self) -> Path:
        return self.root / "colorschemes"

    @property
    def templates_dir(self) -> Path:
        return self.root / "templates"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @classmethod
    def locate(cls, start: Path | None = None, fallback: bool = True) -> "Project":
        """Find the project root at ``start`` or any of its ancestors.

        A directory qualifies when it contains ``config/general.yml`` and
        ``templates/``. With ``fallback`` (the default), falls back to the
        installed checkout (the repo this package lives in) so ``interdot``
        works from anywhere; pass ``fallback=False`` for an explicit
        ``--directory`` so a wrong path errors instead of silently theming
        this checkout.
        """
        candidates = []
        if start is not None:
            start = start.resolve()
            candidates.extend([start, *start.parents])
        if fallback:
            candidates.append(Path(__file__).resolve().parent.parent)
        for candidate in candidates:
            if (candidate / "config" / "general.yml").is_file() and (
                candidate / "templates"
            ).is_dir():
                return cls(root=candidate)
        where = f" at or above {start}" if start is not None else ""
        raise ConfigError(
            "Could not locate an interdotensional project"
            f"{where} (a directory containing config/general.yml and templates/)."
        )


def load_yaml(path: Path):
    """Load a YAML file with errors phrased for the user."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigError(f"File not found: {path}") from None
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}:\n{exc}") from None


def _available(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(p.stem for p in directory.glob("*.yml"))


def available_themes(project: Project) -> list[str]:
    return _available(project.themes_dir)


def available_fonts(project: Project) -> list[str]:
    return _available(project.fonts_dir)


def available_colorschemes(project: Project) -> list[str]:
    return _available(project.colorschemes_dir)


def unknown_choice(kind: str, name: str, available: list[str]) -> ConfigError:
    import difflib

    message = f"Unknown {kind} {name!r}."
    close = difflib.get_close_matches(name, available, n=3)
    if close:
        message += f" Did you mean: {', '.join(close)}?"
    if available:
        message += f"\nAvailable {kind}s: {', '.join(available)}"
    return ConfigError(message)


@dataclass
class Context:
    """Fully resolved data ready for template rendering."""

    theme_name: str
    font_name: str
    data: dict
    unresolved: list[tuple[str, str]] = field(default_factory=list)


def load_colorscheme(project: Project, name: str) -> dict:
    path = project.colorschemes_dir / f"{name}.yml"
    if not path.is_file():
        raise unknown_choice("colorscheme", name, available_colorschemes(project))
    colors = load_yaml(path)
    if not isinstance(colors, dict) or not colors:
        raise ConfigError(
            f"Colorscheme {path} is empty or not a mapping of color names to values."
        )
    return colors


def load_theme(project: Project, name: str) -> dict:
    """Load one theme config and attach its palette under ``colors``.

    Tokens are left unsubstituted; the caller decides which palette to
    resolve them against.
    """
    path = project.themes_dir / f"{name}.yml"
    if not path.is_file():
        raise unknown_choice("theme", name, available_themes(project))
    config = load_yaml(path)
    if not isinstance(config, dict):
        raise ConfigError(f"Theme config {path} must be a YAML mapping.")
    if config.get("colors"):
        raise ConfigError(
            f"Theme config {path} must not define `colors:` directly; "
            "palettes live in colorschemes/."
        )
    # A theme may point at a shared palette via `colorscheme:`;
    # by default the palette file matches the theme name.
    config["colors"] = load_colorscheme(project, config.get("colorscheme", name))
    return config


def load_context(
    project: Project,
    theme: str | None = None,
    font: str | None = None,
) -> Context:
    """Build the template context: general config + theme + colorscheme + font,
    with every ``$token$`` reference resolved against the flattened palette.

    ``theme`` / ``font`` override the selection in ``config/general.yml``.
    """
    data = load_yaml(project.general_path)
    if not isinstance(data, dict):
        raise ConfigError(f"{project.general_path} must be a YAML mapping.")

    theme_name = theme or data.get("theme")
    if not isinstance(theme_name, str) or not theme_name:
        raise ConfigError(
            f"No theme selected. Set `theme:` in {project.general_path} "
            "or pass --theme."
        )
    data["theme"] = load_theme(project, theme_name)

    font_name = font or data.get("font")
    if not isinstance(font_name, str) or not font_name:
        raise ConfigError(
            f"No font selected. Set `font:` in {project.general_path} "
            "or pass --font."
        )
    font_path = project.fonts_dir / f"{font_name}.yml"
    if not font_path.is_file():
        raise unknown_choice("font", font_name, available_fonts(project))
    data["font"] = load_yaml(font_path)

    data = substitute_tokens(data, flatten_dict(data["theme"]["colors"]))

    # The counterpart polarity, resolved against ITS OWN palette and exposed as
    # a second `pair` root. `theme.pair` alone is just a name, which is enough
    # for `interdot toggle` but not for a target that must carry both polarities
    # in one artifact - a website stylesheet whose visitors flip light/dark
    # without running interdot. `pair` is None when the theme has no
    # counterpart; the pair's own `pair:` is deliberately not followed.
    pair_name = data["theme"].get("pair")
    if pair_name:
        pair_config = load_theme(project, pair_name)
        data["pair"] = substitute_tokens(
            pair_config, flatten_dict(pair_config["colors"])
        )
    else:
        data["pair"] = None

    unresolved = find_unresolved_tokens(data)

    return Context(
        theme_name=theme_name,
        font_name=font_name,
        data=data,
        unresolved=unresolved,
    )
