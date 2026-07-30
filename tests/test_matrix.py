"""The safety net: every theme x font combination must render cleanly.

A token typo, a missing tool section, or an empty colorscheme in ANY theme
fails here - not weeks later when that theme is next activated.
"""

from pathlib import Path

import pytest

from interdotensional.check import check_combination, check_project_warnings
from interdotensional.config import Project, available_fonts, available_themes
from interdotensional.filters import darken

_REPO = Project(root=Path(__file__).resolve().parent.parent)


@pytest.mark.parametrize("font", available_fonts(_REPO))
@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_theme_font_combination_renders(repo_project, theme, font):
    report = check_combination(repo_project, theme, font)
    assert report.errors == []


def test_project_hygiene(repo_project):
    assert check_project_warnings(repo_project) == []


def test_rendered_output_carries_palette_colors(repo_project):
    """Pin the token -> template wiring: the active theme's palette colors
    must actually appear in rendered output."""
    from interdotensional.config import load_context, load_yaml
    from interdotensional.generate import render_all

    context = load_context(repo_project)
    palette = context.data["theme"]["colors"]
    fzf = next(
        r for r in render_all(repo_project, context)
        if r.rel_output == "fzf/fzf-colors.sh"
    )
    fg = context.data["theme"]["tools"]["fzf"]["fg"]
    assert fg in fzf.content
    assert fg in palette.values()


def test_interdimux_colors_reach_tmux_conf(repo_project):
    """A theme's interdimux palette must render into the tmux config as
    @interdimux-color-* options, with underscore keys hyphenated."""
    from interdotensional.config import load_context
    from interdotensional.generate import render_all

    context = load_context(repo_project, theme="gruvbox-material-dark")
    interdimux = context.data["theme"]["tools"]["interdimux"]
    tmux = next(
        r for r in render_all(repo_project, context)
        if r.rel_output == "tmux/.tmux.conf"
    )
    assert f'@interdimux-color-accent "{interdimux["accent"]}"' in tmux.content
    assert f'@interdimux-color-current-bg "{interdimux["current_bg"]}"' in tmux.content


WEB_ROLES = (
    "bg", "bg_deep", "panel", "border", "faint",
    "fg", "fg_strong", "muted", "dim",
    "accent", "accent2", "success", "info", "special", "warning", "danger",
    # Not from leaf: pane chrome and selection come from tools.tmux.colors, and
    # prompt_dir is an opt-in tools.web key that falls back to leaf's `info`.
    # All five must still resolve for every theme, because a visitor cannot run
    # interdot to fix a missing one.
    "pane_active", "pane_border", "select_fg", "select_bg", "prompt_dir",
)


def _web_css(project, context) -> str:
    from interdotensional.generate import render_all

    return next(
        r for r in render_all(project, context)
        if r.rel_output == "web/interdot-theme.css"
    ).content


@pytest.mark.parametrize("font", available_fonts(_REPO))
@pytest.mark.parametrize("theme", available_themes(_REPO))
def test_web_stylesheet_carries_every_role(repo_project, theme, font):
    """The website is the one target whose output ships to people who cannot
    run interdot, so a missing role there is a broken page for a visitor rather
    than a config the author can regenerate. Every theme must emit all 16."""
    from interdotensional.config import load_context

    css = _web_css(repo_project, load_context(repo_project, theme=theme, font=font))
    for role in WEB_ROLES:
        prop = f"--id-{role.replace('_', '-')}"
        assert f"{prop}: #" in css, f"{theme}/{font} is missing {prop}"
    assert f'--id-author-theme: "{theme}";' in css


@pytest.mark.parametrize(
    "theme, blocks",
    [("gruvbox-material-light", 4), ("gruvbox-material-dark", 4), ("nord", 1)],
)
def test_web_stylesheet_ships_both_polarities_only_when_paired(
    repo_project, theme, blocks
):
    """A visitor's light/dark toggle cannot re-run interdot, so a paired theme
    ships BOTH palettes: the active one on :root, the counterpart under the
    media query, and both again under [data-theme] so a manual choice beats the
    OS preference in either direction - four blocks. An unpaired theme has no
    counterpart palette to emit, so it must stay at one."""
    from interdotensional.config import load_context

    css = _web_css(repo_project, load_context(repo_project, theme=theme))
    assert css.count("--id-bg: ") == blocks
    if blocks == 1:
        assert "prefers-color-scheme" not in css
        assert "[data-theme" not in css
    else:
        pair = load_context(repo_project, theme=theme).data["pair"]
        assert f"@media (prefers-color-scheme: {pair['polarity']})" in css
        assert ":root:not([data-theme])" in css
        assert f'--id-bg: {pair["tools"]["leaf"]["colors"]["bg"]};' in css


def test_web_text_darken_prefers_the_web_map(repo_project):
    """The web needs more contrast than leaf's terminal chips: a tools.web
    text_darken must win over tools.leaf's, and neither may touch a dark theme
    (which has no map at all and must emit its palette untouched)."""
    from interdotensional.config import load_context

    context = load_context(repo_project, theme="gruvbox-material-light")
    css = _web_css(repo_project, context)
    leaf = context.data["theme"]["tools"]["leaf"]
    raw_accent = leaf["colors"]["accent"]
    assert f"--id-accent: {raw_accent};" not in css
    assert f'--id-accent: {darken(raw_accent, leaf["text_darken"]["accent"])};' not in css
    web_darken = context.data["theme"]["tools"]["web"]["text_darken"]["accent"]
    assert f"--id-accent: {darken(raw_accent, web_darken)};" in css

    dark = context.data["pair"]["tools"]["leaf"]["colors"]
    assert f'--id-accent: {dark["accent"]};' in css


def test_tmux_renders_single_output_no_partial_leak(repo_project):
    """tmux is the only multi-file tool: its config is assembled from partials
    under templates/tmux/parts/ that are `{% include %}`d, not discovered. Those
    partials MUST NOT end in .j2, or discover_templates() would emit each as its
    own junk output under output/tmux/parts/ (which is the live symlinked config
    dir). Rendering must yield exactly one tmux/* output — the assembled conf —
    and that conf must still end on the TPM bootstrap line, which tmux requires
    to run last (it sources every plugin's @-options inline)."""
    from interdotensional.config import load_context
    from interdotensional.generate import discover_templates, render_all

    templates = discover_templates(repo_project)
    assert not any(t.startswith("tmux/parts/") for t in templates), (
        f"a tmux partial leaked into discovery (rename it off .j2): {templates}"
    )

    context = load_context(repo_project, theme="gruvbox-material-dark")
    tmux_outputs = [
        r for r in render_all(repo_project, context)
        if r.rel_output.startswith("tmux/")
    ]
    assert [r.rel_output for r in tmux_outputs] == ["tmux/.tmux.conf"]
    assert tmux_outputs[0].content.rstrip().endswith(
        "run '~/.tmux/plugins/tpm/tpm'"
    )
