import pytest

from interdotensional.cli import main


def run(capsys, *argv):
    code = main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_unknown_command_suggests(capsys):
    code, _, err = run(capsys, "generat")
    assert code == 2
    assert "did you mean: interdot generate" in err


def test_global_flags_work_before_subcommand(capsys, make_project):
    # git-style: `interdot -C DIR list` and `interdot list -C DIR` both work.
    project = make_project()
    before, out_before, _ = run(capsys, "-C", str(project.root), "list", "themes")
    after, out_after, _ = run(capsys, "list", "themes", "-C", str(project.root))
    assert before == after == 0
    assert out_before == out_after
    assert "mono" in out_before


def test_bad_directory_errors_cleanly(capsys, tmp_path):
    code, _, err = run(capsys, "-C", str(tmp_path / "nope"), "status")
    assert code == 1
    assert "Could not locate" in err
    assert "Traceback" not in err


def test_list_themes(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "list", "themes", "-C", str(project.root))
    assert code == 0
    assert "mono" in out
    assert "*" in out  # active theme marked


def test_status_reports_stale_then_fresh(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "status", "-C", str(project.root))
    assert code == 0
    assert "stale" in out

    run(capsys, "generate", "-C", str(project.root))
    code, out, _ = run(capsys, "status", "-C", str(project.root))
    assert code == 0
    assert "up to date" in out


def test_generate_writes_output(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "generate", "-C", str(project.root))
    assert code == 0
    assert "1 created" in out
    assert (project.output_dir / "app" / "app.conf").read_text() == (
        "accent #ff0000\nfamily Plain"
    )


def test_generate_dry_run_writes_nothing(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "generate", "-n", "-C", str(project.root))
    assert code == 0
    assert "dry run" in out
    assert not project.output_dir.exists()


def test_generate_diff(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "generate", "-n", "--diff", "-C", str(project.root))
    assert code == 0
    assert "+accent #ff0000" in out


def test_generate_refuses_unresolved_tokens(capsys, make_project):
    project = make_project(
        {
            "config/themes/mono.yml": (
                'name: "mono"\ntools:\n  app:\n'
                '    accent: "$typo$"\n    label: "hi"\n'
            )
        }
    )
    code, _, err = run(capsys, "generate", "-C", str(project.root))
    assert code == 1
    assert "$typo$" in err
    assert not project.output_dir.exists()


def test_generate_unknown_theme(capsys, make_project):
    project = make_project()
    code, _, err = run(capsys, "generate", "--theme", "mono2", "-C", str(project.root))
    assert code == 1
    assert "Did you mean" in err


def test_check_passes_on_clean_project(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "check", "-C", str(project.root))
    assert code == 0
    assert "1 ok, 0 failed" in out


def test_check_fails_on_broken_theme(capsys, make_project):
    project = make_project(
        {"templates/app/app.conf.j2": "{{ theme.tools.app.nope }}"}
    )
    code, out, _ = run(capsys, "check", "-C", str(project.root))
    assert code == 1
    assert "0 ok, 1 failed" in out


def test_switch_updates_general_yml_preserving_comments(capsys, make_project):
    project = make_project(
        {
            "config/general.yml": (
                "# my precious comment\n"
                'theme: "mono"\n'
                'font: "plain"\n'
            ),
            "config/themes/second.yml": (
                'name: "second"\ncolorscheme: "mono"\n'
                "tools:\n  app:\n"
                '    accent: "$bg$"\n    label: "hi"\n'
            ),
        }
    )
    code, _, _ = run(capsys, "switch", "second", "-C", str(project.root))
    assert code == 0
    text = project.general_path.read_text()
    assert "# my precious comment" in text
    assert 'theme: "second"' in text
    assert (project.output_dir / "app" / "app.conf").read_text().startswith(
        "accent #101010"
    )


def test_switch_unknown_theme(capsys, make_project):
    project = make_project()
    code, _, err = run(capsys, "switch", "nope", "-C", str(project.root))
    assert code == 1
    assert "Unknown theme" in err


def test_toggle_follows_pair(capsys, make_project):
    project = make_project(
        {
            "config/themes/mono.yml": (
                'name: "mono"\npair: "second"\n'
                "tools:\n  app:\n"
                '    accent: "$red$"\n    label: "hi"\n'
            ),
            "config/themes/second.yml": (
                'name: "second"\ncolorscheme: "mono"\npair: "mono"\n'
                "tools:\n  app:\n"
                '    accent: "$bg$"\n    label: "hi"\n'
            ),
        }
    )
    code, _, _ = run(capsys, "toggle", "-C", str(project.root))
    assert code == 0
    assert 'theme: "second"' in project.general_path.read_text()

    code, _, _ = run(capsys, "toggle", "-C", str(project.root))
    assert code == 0
    assert 'theme: "mono"' in project.general_path.read_text()


def test_toggle_without_pair_errors(capsys, make_project):
    project = make_project()
    code, _, err = run(capsys, "toggle", "-C", str(project.root))
    assert code == 1
    assert "no `pair:`" in err


def test_hooks_run_after_changes(capsys, make_project, tmp_path):
    marker = tmp_path / "hook-ran"
    project = make_project(
        {
            "config/general.yml": (
                'theme: "mono"\nfont: "plain"\n'
                "hooks:\n"
                f'  - "touch {marker}"\n'
            )
        }
    )
    code, _, _ = run(capsys, "generate", "-C", str(project.root))
    assert code == 0
    assert marker.exists()

    # Nothing changed on the second run -> hooks skipped.
    marker.unlink()
    run(capsys, "generate", "-C", str(project.root))
    assert not marker.exists()


def test_failing_hook_sets_exit_code_and_warns(capsys, make_project):
    project = make_project(
        {
            "config/general.yml": (
                'theme: "mono"\nfont: "plain"\n'
                'hooks: ["exit 3"]\n'
            )
        }
    )
    code, _, err = run(capsys, "generate", "-C", str(project.root))
    assert code == 1
    assert "hook failed with exit code 3" in err


def test_scalar_hook_string_is_run_as_one_command(capsys, make_project, tmp_path):
    marker = tmp_path / "scalar-hook-ran"
    project = make_project(
        {
            "config/general.yml": (
                'theme: "mono"\nfont: "plain"\n'
                f'hooks: "touch {marker}"\n'  # a scalar, not a list
            )
        }
    )
    code, _, _ = run(capsys, "generate", "-C", str(project.root))
    assert code == 0
    assert marker.exists()  # ran once, not once per character


def test_hooks_skipped_with_no_hooks_flag(capsys, make_project, tmp_path):
    marker = tmp_path / "hook-ran"
    project = make_project(
        {
            "config/general.yml": (
                'theme: "mono"\nfont: "plain"\n'
                f'hooks: ["touch {marker}"]\n'
            )
        }
    )
    code, _, _ = run(capsys, "generate", "--no-hooks", "-C", str(project.root))
    assert code == 0
    assert not marker.exists()


def test_preview(capsys, make_project):
    project = make_project()
    code, out, _ = run(capsys, "preview", "mono", "-C", str(project.root))
    assert code == 0
    assert "#ff0000" in out
    assert "red" in out


def test_preview_all(capsys, make_project):
    project = make_project({"colorschemes/second.yml": 'blue: "#0000ff"\n'})
    code, out, _ = run(capsys, "preview", "--all", "-C", str(project.root))
    assert code == 0
    assert "#ff0000" in out and "#0000ff" in out


def test_check_scoped_by_theme_flag(capsys, make_project):
    project = make_project(
        {"config/themes/broken.yml": 'name: "broken"\ntools:\n  app:\n    label: "hi"\n'}
    )
    # Scoped to the good theme -> passes even though a broken theme exists.
    code, out, _ = run(capsys, "check", "-t", "mono", "-C", str(project.root))
    assert code == 0
    assert "1 ok, 0 failed" in out


def test_generate_diff_on_real_write(capsys, make_project):
    project = make_project()
    run(capsys, "generate", "-C", str(project.root))  # first write
    (project.root / "colorschemes" / "mono.yml").write_text(
        'red: "#00ff00"\nbg: "#101010"\n'
    )
    code, out, _ = run(capsys, "generate", "--diff", "-C", str(project.root))
    assert code == 0
    assert "-accent #ff0000" in out and "+accent #00ff00" in out


def test_link_dry_run_and_apply(capsys, make_project, tmp_path):
    target = tmp_path / "dest" / ".appconf"
    project = make_project(
        {
            "config/general.yml": (
                'theme: "mono"\nfont: "plain"\n'
                "links:\n"
                f'  "{target}": "app/app.conf"\n'
            )
        }
    )
    run(capsys, "generate", "-C", str(project.root))

    code, out, _ = run(capsys, "link", "-n", "-C", str(project.root))
    assert code == 0
    assert "would link" in out
    assert not target.exists()

    code, out, _ = run(capsys, "link", "-C", str(project.root))
    assert code == 0
    assert target.is_symlink()
