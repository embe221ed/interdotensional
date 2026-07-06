"""The safety net: every theme x font combination must render cleanly.

A token typo, a missing tool section, or an empty colorscheme in ANY theme
fails here - not weeks later when that theme is next activated.
"""

from pathlib import Path

import pytest

from interdotensional.check import check_combination, check_project_warnings
from interdotensional.config import Project, available_fonts, available_themes

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
