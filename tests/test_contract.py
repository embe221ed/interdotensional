"""Every theme carries the gruvbox contract.

gruvbox-material-dark/-light are the reference themes: the token vocabulary
their colorschemes define and the tool sections their configs carry are what
"a theme works" means in this repo. This pins that every other theme keeps up,
so a new tool section or token added to gruvbox alone fails here instead of
leaving the other themes silently half-themed.
"""

from pathlib import Path

import pytest

from interdotensional.config import (
    Project,
    available_themes,
    load_colorscheme,
    load_context,
    load_yaml,
)
from interdotensional.tokens import flatten_dict

_REPO = Project(root=Path(__file__).resolve().parent.parent)
_REFERENCE = {"dark": "gruvbox-material-dark", "light": "gruvbox-material-light"}

# The palette vocabulary every colorscheme fills (the gruvbox names; the three
# legacy bg_* tokens in the gruvbox files are unused by any template and are
# deliberately not part of it).
CONTRACT_TOKENS = (
    "red", "orange", "yellow", "green", "aqua", "blue", "purple",
    "pink", "peach", "terracotta", "maroon",
    "fg_primary", "fg_secondary", "fg_muted", "fg_dim", "fg_faint",
    "border", "panel_raised", "panel", "panel_inset",
    "bg_primary", "bg_deep", "bg_abyss",
    "grey0", "grey1", "grey2", "fg0", "fg1",
)

CATPPUCCIN_KEYS = (
    "rosewater", "flamingo", "pink", "mauve", "red", "maroon", "peach", "yellow",
    "green", "teal", "sky", "sapphire", "blue", "lavender", "text", "subtext1",
    "subtext0", "overlay2", "overlay1", "overlay0", "surface2", "surface1",
    "surface0", "base", "mantle", "crust",
)


def _is_hex(value) -> bool:
    v = str(value)
    return len(v) == 7 and v[0] == "#" and all(c in "0123456789abcdef" for c in v[1:])


def _key_paths(mapping, prefix=""):
    """Dotted leaf paths of a nested mapping (values ignored)."""
    paths = set()
    for key, value in mapping.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict) and value:
            paths |= _key_paths(value, path)
        else:
            paths.add(path)
    return paths


def _theme(name):
    return load_yaml(_REPO.themes_dir / f"{name}.yml")


@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_colorscheme_fills_the_contract_vocabulary(theme):
    config = _theme(theme)
    palette = flatten_dict(load_colorscheme(_REPO, config.get("colorscheme", theme)))
    missing = [t for t in CONTRACT_TOKENS if t not in palette]
    assert missing == [], f"{theme}: colorscheme lacks {missing}"
    bad = [t for t in CONTRACT_TOKENS if not _is_hex(palette[t])]
    assert bad == [], f"{theme}: not lower-case #rrggbb: {bad}"


@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_theme_carries_every_gruvbox_tool_section(theme):
    """Same sections and keys as the reference of the same polarity. Only the
    polarity-specific text_darken maps and the nvim override table may differ
    in shape (a native-plugin theme has no override table)."""
    config = _theme(theme)
    polarity = config.get("polarity")
    assert polarity in _REFERENCE, f"{theme}: polarity must be light or dark"
    reference = _theme(_REFERENCE[polarity])

    def shape(cfg):
        return {
            p for p in _key_paths(cfg["tools"], "tools")
            if ".text_darken." not in p
            and not p.startswith("tools.nvim.catppuccin_overrides.")
            # kitty is an empty block (include <theme>.conf) or {name: ...}
            # where a differently named theme file exists; both are the slot.
            and not p.startswith("tools.kitty")
        }

    assert "kitty" in config["tools"], f"{theme}: no tools.kitty section"
    missing = sorted(shape(reference) - shape(config))
    assert missing == [], f"{theme}: missing vs {_REFERENCE[polarity]}: {missing}"


@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_theme_has_a_light_dark_pair(theme):
    config = _theme(theme)
    pair = config.get("pair")
    assert pair, f"{theme}: no pair: declared"
    other = _theme(pair)
    assert other.get("pair") == theme, f"{pair} does not pair back to {theme}"
    assert {config["polarity"], other["polarity"]} == {"light", "dark"}
    # toggle must not change the editor's semantic layout: same engine both ways
    engine = lambda cfg: (cfg["tools"]["nvim"]["colorscheme"], cfg["tools"]["nvim"].get("scheme"))
    assert engine(config) == engine(other), f"{theme} and {pair} use different nvim engines"


@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_terminal_facing_colors_are_palette_hex(theme):
    """zsh, colorls and interdimux all render truecolor; a 256-colour index or
    an X11 colour name there is a drift away from the palette."""
    tools = load_context(_REPO, theme=theme).data["theme"]["tools"]
    offenders = []
    for key, value in tools["zsh"]["colors"].items():
        if not _is_hex(value):
            offenders.append(f"zsh.colors.{key}={value!r}")
    for key, value in tools["colorls"].items():
        if not _is_hex(value):
            offenders.append(f"colorls.{key}={value!r}")
    for key, value in tools["interdimux"].items():
        if not _is_hex(value):
            offenders.append(f"interdimux.{key}={value!r}")
    assert offenders == [], f"{theme}: {offenders}"


@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_catppuccin_engine_themes_override_the_full_palette(theme):
    tools = load_context(_REPO, theme=theme).data["theme"]["tools"]
    nvim = tools["nvim"]
    if nvim["colorscheme"] != "catppuccin":
        pytest.skip("native colorscheme plugin")
    overrides = nvim.get("catppuccin_overrides")
    assert overrides, f"{theme}: catppuccin engine without catppuccin_overrides"
    assert tuple(overrides) == CATPPUCCIN_KEYS, f"{theme}: override keys must be the 26 catppuccin keys, in order"
    bad = {k: v for k, v in overrides.items() if not _is_hex(v)}
    assert bad == {}, f"{theme}: unresolved or non-hex overrides {bad}"
    assert nvim["scheme"] == "gruvbox-material", (
        f"{theme}: overrides are only read by the gruvbox-material scheme file"
    )
    for field, key in nvim["fields"].items():
        assert key == "NONE" or key in CATPPUCCIN_KEYS, f"{theme}: fields.{field}={key!r}"
