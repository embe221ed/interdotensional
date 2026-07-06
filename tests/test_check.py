import pytest

from interdotensional.check import (
    check_combination,
    check_matrix,
    check_project_warnings,
)


def test_matrix_scopes_to_requested_theme_and_font(make_project):
    project = make_project(
        {
            "config/themes/second.yml": (
                'name: "second"\ncolorscheme: "mono"\n'
                "tools:\n  app:\n"
                '    accent: "$bg$"\n    label: "hi"\n'
            ),
            "config/fonts/second.yml": 'family: "Second"\nsize: 10\n',
        }
    )
    # Full matrix: 2 themes x 2 fonts.
    assert len(check_matrix(project)) == 4
    # Scoped: one theme, one font.
    scoped = check_matrix(project, themes=["mono"], fonts=["plain"])
    assert len(scoped) == 1
    assert scoped[0].theme == "mono" and scoped[0].font == "plain"


def test_check_combination_reports_unresolved_token(make_project):
    project = make_project(
        {
            "config/themes/mono.yml": (
                'name: "mono"\ntools:\n  app:\n'
                '    accent: "$ghost$"\n    label: "hi"\n'
            )
        }
    )
    report = check_combination(project, "mono", "plain")
    assert not report.ok
    assert any("$ghost$" in e for e in report.errors)


def test_hygiene_clean_project_has_no_warnings(make_project):
    assert check_project_warnings(make_project()) == []


def test_hygiene_flags_orphan_colorscheme(make_project):
    project = make_project({"colorschemes/unused.yml": 'x: "#000000"\n'})
    warnings = check_project_warnings(project)
    assert any("unused" in w and "not used" in w for w in warnings)


def test_hygiene_flags_non_hex_palette_value(make_project):
    project = make_project(
        {"colorschemes/mono.yml": 'red: "#ff0000"\nbg: "not-a-color"\n'}
    )
    warnings = check_project_warnings(project)
    assert any("not a hex color" in w for w in warnings)


def test_hygiene_flags_missing_colorscheme_for_indirection(make_project):
    project = make_project(
        {
            "config/themes/mono.yml": (
                'name: "mono"\ncolorscheme: "ghost"\n'
                "tools:\n  app:\n"
                '    accent: "$red$"\n    label: "hi"\n'
            )
        }
    )
    warnings = check_project_warnings(project)
    assert any("ghost" in w and "does not exist" in w for w in warnings)
