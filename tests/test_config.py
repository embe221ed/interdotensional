import pytest

from interdotensional.config import (
    ConfigError,
    Project,
    available_fonts,
    available_themes,
    load_context,
)


def test_load_context_resolves_tokens(make_project):
    project = make_project()
    context = load_context(project)
    assert context.theme_name == "mono"
    assert context.font_name == "plain"
    assert context.data["theme"]["tools"]["app"]["accent"] == "#ff0000"
    assert context.unresolved == []


def test_unknown_theme_suggests_close_match(make_project):
    project = make_project()
    with pytest.raises(ConfigError, match="Did you mean.*mono"):
        load_context(project, theme="mono2")


def test_unknown_theme_lists_available(make_project):
    project = make_project()
    with pytest.raises(ConfigError, match="Available themes: mono"):
        load_context(project, theme="zzz")


def test_unknown_font(make_project):
    project = make_project()
    with pytest.raises(ConfigError, match="Unknown font"):
        load_context(project, font="nope")


def test_theme_config_must_not_define_colors(make_project):
    project = make_project(
        {"config/themes/mono.yml": 'name: "mono"\ncolors:\n  red: "#000"\n'}
    )
    with pytest.raises(ConfigError, match="must not define `colors:`"):
        load_context(project)


def test_empty_colorscheme_is_an_error(make_project):
    project = make_project({"colorschemes/mono.yml": "# just a comment\n"})
    with pytest.raises(ConfigError, match="empty or not a mapping"):
        load_context(project)


def test_colorscheme_indirection(make_project):
    project = make_project(
        {
            "config/themes/mono.yml": (
                'name: "mono"\ncolorscheme: "shared"\n'
                "tools:\n  app:\n"
                '    accent: "$red$"\n    label: "hi"\n'
            ),
            "colorschemes/shared.yml": 'red: "#123456"\n',
        }
    )
    context = load_context(project)
    assert context.data["theme"]["tools"]["app"]["accent"] == "#123456"


def test_missing_theme_key(make_project):
    project = make_project({"config/general.yml": 'font: "plain"\n'})
    with pytest.raises(ConfigError, match="No theme selected"):
        load_context(project)


def test_invalid_yaml_reports_filename(make_project):
    project = make_project({"config/themes/mono.yml": "name: [unclosed\n"})
    with pytest.raises(ConfigError, match="Invalid YAML.*mono.yml"):
        load_context(project)


def test_unresolved_tokens_are_collected(make_project):
    project = make_project(
        {
            "config/themes/mono.yml": (
                'name: "mono"\ntools:\n  app:\n'
                '    accent: "$nonexistent$"\n    label: "hi"\n'
            )
        }
    )
    context = load_context(project)
    assert context.unresolved == [
        ("theme.tools.app.accent", "$nonexistent$")
    ]


def test_locate_finds_root_from_subdirectory(make_project):
    project = make_project()
    located = Project.locate(project.root / "config" / "themes")
    assert located.root == project.root


def test_available_listings(make_project):
    project = make_project()
    assert available_themes(project) == ["mono"]
    assert available_fonts(project) == ["plain"]


def test_locate_explicit_directory_does_not_fall_back(tmp_path):
    with pytest.raises(ConfigError, match="Could not locate"):
        Project.locate(tmp_path, fallback=False)
