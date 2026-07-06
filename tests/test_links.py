import pytest

from interdotensional.config import Project
from interdotensional.links import apply_links, plan_links


@pytest.fixture
def linked_project(make_project):
    project = make_project()
    source = project.output_dir / "app" / "app.conf"
    source.parent.mkdir(parents=True)
    source.write_text("generated")
    return project, source


def test_plan_missing_source(make_project, tmp_path):
    project = make_project()
    results = plan_links(project, {str(tmp_path / "dest"): "app/app.conf"})
    assert results[0].status == "missing-source"


def test_create_and_ok(linked_project, tmp_path):
    project, source = linked_project
    target = tmp_path / "home" / ".appconf"
    links = {str(target): "app/app.conf"}

    results = plan_links(project, links)
    assert results[0].status == "created"
    apply_links(results)
    assert target.is_symlink() and target.resolve() == source

    assert plan_links(project, links)[0].status == "ok"


def test_retarget_wrong_symlink(linked_project, tmp_path):
    project, source = linked_project
    other = tmp_path / "other"
    other.write_text("x")
    target = tmp_path / ".appconf"
    target.symlink_to(other)

    results = plan_links(project, {str(target): "app/app.conf"})
    assert results[0].status == "retargeted"
    apply_links(results)
    assert target.resolve() == source


def test_conflict_requires_force(linked_project, tmp_path):
    project, source = linked_project
    target = tmp_path / ".appconf"
    target.write_text("precious hand-written config")

    results = plan_links(project, {str(target): "app/app.conf"})
    assert results[0].status == "conflict"

    apply_links(results, force=False)
    assert not target.is_symlink()
    assert target.read_text() == "precious hand-written config"

    results = plan_links(project, {str(target): "app/app.conf"})
    apply_links(results, force=True)
    assert target.is_symlink() and target.resolve() == source
    backup = tmp_path / ".appconf.bak"
    assert backup.read_text() == "precious hand-written config"
