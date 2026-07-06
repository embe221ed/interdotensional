import pytest

from interdotensional.config import load_context
from interdotensional.generate import (
    GenerationError,
    compare_with_disk,
    diff_results,
    discover_templates,
    render_all,
    try_render_all,
    write_results,
)

import interdotensional.generate as generate_mod


def test_discovery_convention(make_project):
    project = make_project(
        {"templates/tool/.hidden.conf.j2": "x", "templates/tool/plain.txt": "not a template"}
    )
    templates = discover_templates(project)
    assert templates == ["app/app.conf.j2", "tool/.hidden.conf.j2"]


def test_render_produces_expected_content(make_project):
    project = make_project()
    results = render_all(project, load_context(project))
    assert len(results) == 1
    assert results[0].rel_output == "app/app.conf"
    assert results[0].content == "accent #ff0000\nfamily Plain"


def test_missing_variable_fails_loudly_with_template_name(make_project):
    project = make_project(
        {"templates/app/app.conf.j2": "{{ theme.tools.app.missing_key }}"}
    )
    with pytest.raises(GenerationError, match="app/app.conf.j2"):
        render_all(project, load_context(project))


def test_try_render_all_collects_every_error(make_project):
    project = make_project(
        {
            "templates/app/app.conf.j2": "{{ nope_one }}",
            "templates/other/x.conf.j2": "{{ nope_two }}",
        }
    )
    results, errors = try_render_all(project, load_context(project))
    assert results == []
    assert len(errors) == 2


def test_write_and_status_lifecycle(make_project):
    project = make_project()
    context = load_context(project)

    results = render_all(project, context)
    compare_with_disk(project, results)
    assert results[0].status == "created"
    write_results(project, results)
    out = project.output_dir / "app" / "app.conf"
    assert out.read_text() == "accent #ff0000\nfamily Plain"

    # Second run: byte-identical -> unchanged, file untouched (mtime preserved).
    results = render_all(project, context)
    compare_with_disk(project, results)
    assert results[0].status == "unchanged"
    mtime = out.stat().st_mtime_ns
    write_results(project, results)
    assert out.stat().st_mtime_ns == mtime

    # Source change -> updated.
    (project.root / "colorschemes" / "mono.yml").write_text('red: "#00ff00"\nbg: "#101010"\n')
    results = render_all(project, load_context(project))
    compare_with_disk(project, results)
    assert results[0].status == "updated"
    write_results(project, results)
    assert "accent #00ff00" in out.read_text()


def test_diff_only_covers_changed_files(make_project):
    project = make_project()
    context = load_context(project)
    results = render_all(project, context)
    compare_with_disk(project, results)
    diff = diff_results(project, results)
    assert "b/output/app/app.conf" in diff
    assert "+accent #ff0000" in diff

    write_results(project, results)
    results = render_all(project, context)
    compare_with_disk(project, results)
    assert diff_results(project, results) == ""


def test_no_temp_files_left_behind(make_project):
    project = make_project()
    results = render_all(project, load_context(project))
    compare_with_disk(project, results)
    write_results(project, results)
    leftovers = list(project.output_dir.rglob("*.tmp"))
    assert leftovers == []


def test_write_is_atomic_on_failure(make_project, monkeypatch):
    """A crash during the rename must leave the existing file intact and no
    stray temp file behind - output/ holds the user's LIVE symlinked config."""
    project = make_project()
    context = load_context(project)
    out = project.output_dir / "app" / "app.conf"
    out.parent.mkdir(parents=True)
    out.write_text("original contents")

    def boom(src, dst):
        raise OSError("simulated crash during rename")

    monkeypatch.setattr(generate_mod.os, "replace", boom)
    results = render_all(project, context)
    with pytest.raises(OSError, match="simulated crash"):
        write_results(project, results)

    # Original file untouched, no half-written temp file left behind.
    assert out.read_text() == "original contents"
    assert list(project.output_dir.rglob("*.tmp")) == []


def test_diff_survives_undecodable_existing_file(make_project):
    project = make_project()
    context = load_context(project)
    out = project.output_dir / "app" / "app.conf"
    out.parent.mkdir(parents=True)
    out.write_bytes(b"\xff\xfe\x00 not utf-8")

    results = render_all(project, context)
    compare_with_disk(project, results)
    assert results[0].status == "updated"
    # Must not raise UnicodeDecodeError; shows the full new file as additions.
    diff = diff_results(project, results)
    assert "+accent #ff0000" in diff


def test_color_filters_available_in_templates(make_project):
    project = make_project(
        {
            "templates/app/app.conf.j2": (
                "{{ theme.tools.app.accent | darken(10) }} "
                "{{ theme.tools.app.accent | strip_hash }}"
            )
        }
    )
    results = render_all(project, load_context(project))
    darkened, stripped = results[0].content.split()
    assert darkened.startswith("#") and darkened != "#ff0000"
    assert stripped == "ff0000"
