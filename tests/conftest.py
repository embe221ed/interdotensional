from pathlib import Path

import pytest

from interdotensional.config import Project

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_FILES = {
    "config/general.yml": (
        'theme: "mono"\n'
        'font: "plain"\n'
        "ui:\n"
        '  border: "none"\n'
    ),
    "config/themes/mono.yml": (
        'name: "mono"\n'
        "tools:\n"
        "  app:\n"
        '    accent: "$red$"\n'
        '    label: "hi"\n'
    ),
    "config/fonts/plain.yml": 'family: "Plain"\nsize: 12\n',
    "colorschemes/mono.yml": 'red: "#ff0000"\nbg: "#101010"\n',
    "templates/app/app.conf.j2": (
        "accent {{ theme.tools.app.accent }}\n"
        "family {{ font.family }}"
    ),
}


@pytest.fixture(scope="session")
def repo_project() -> Project:
    """The real repository, used read-only (never generate into it)."""
    return Project(root=REPO_ROOT)


@pytest.fixture
def make_project(tmp_path):
    """Factory for a tiny synthetic project safe to mutate or break."""

    def _make(files: dict[str, str] | None = None) -> Project:
        merged = {**DEFAULT_FILES, **(files or {})}
        for rel, content in merged.items():
            if content is None:
                continue
            path = tmp_path / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return Project(root=tmp_path)

    return _make
