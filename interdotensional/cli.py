"""interdot - command-line interface.

``interdot`` with no arguments shows the active theme/font and whether
output/ is stale; ``interdot generate`` renders. Subcommands add the rest:
check, list, preview, switch, toggle, link.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from . import __version__
from .check import check_matrix, check_project_warnings
from .config import (
    ConfigError,
    Project,
    available_colorschemes,
    available_fonts,
    available_themes,
    load_context,
    load_yaml,
    unknown_choice,
)
from .generate import (
    GenerationError,
    compare_with_disk,
    diff_results,
    render_all,
    write_results,
)
from .links import apply_links, plan_links
from .preview import render_palette

COMMANDS = ("status", "generate", "check", "list", "preview", "switch", "toggle", "link")

_STATUS_ICONS = {"created": "+", "updated": "~", "unchanged": "="}


class UI:
    def __init__(self, quiet: bool = False, verbose: bool = False, color: str = "auto"):
        self.quiet = quiet
        self.verbose = verbose
        if color == "auto":
            self.color = (
                sys.stdout.isatty()
                and "NO_COLOR" not in os.environ
                and os.environ.get("TERM") != "dumb"
            )
        else:
            self.color = color == "always"

    def sty(self, code: str, text: str) -> str:
        return f"\x1b[{code}m{text}\x1b[0m" if self.color else text

    def say(self, text: str = "") -> None:
        if not self.quiet:
            print(text)

    def detail(self, text: str) -> None:
        if self.verbose:
            print(self.sty("2", text))

    def warn(self, text: str) -> None:
        print(self.sty("33", f"warning: {text}"), file=sys.stderr)

    def error(self, text: str) -> None:
        print(self.sty("31", f"error: {text}"), file=sys.stderr)


def _print_file_statuses(ui: UI, results) -> None:
    width = max((len(r.rel_output) for r in results), default=0)
    for result in results:
        icon = _STATUS_ICONS[result.status]
        line = f"  {icon} {result.rel_output:<{width}}  {result.status}"
        if result.status == "unchanged":
            ui.say(ui.sty("2", line))
        else:
            ui.say(ui.sty("32", line))


def _summary(results) -> str:
    counts = {status: 0 for status in _STATUS_ICONS}
    for result in results:
        counts[result.status] += 1
    parts = [f"{n} {status}" for status, n in counts.items() if n]
    return f"{len(results)} files: " + ", ".join(parts)


def _normalize_hooks(hooks) -> list[str]:
    """Accept either a single command string or a list of commands.

    Without this, a scalar ``hooks: "echo hi"`` would iterate character by
    character and run each letter as its own shell command.
    """
    if hooks is None:
        return []
    if isinstance(hooks, str):
        return [hooks]
    if isinstance(hooks, list) and all(isinstance(h, str) for h in hooks):
        return hooks
    raise ConfigError(
        "`hooks:` in general.yml must be a command string or a list of "
        f"command strings, not {type(hooks).__name__}."
    )


def _run_hooks(ui: UI, project: Project, hooks) -> int:
    failures = 0
    for hook in hooks:
        ui.say(f"  hook: {hook}")
        proc = subprocess.run(hook, shell=True, cwd=project.root)
        if proc.returncode != 0:
            ui.warn(f"hook failed with exit code {proc.returncode}: {hook}")
            failures += 1
    return failures


def cmd_status(project: Project, args, ui: UI) -> int:
    general = load_yaml(project.general_path) or {}
    print(f"interdotensional {__version__} · {project.root}")
    print(f"  theme: {ui.sty('1', str(general.get('theme')))}")
    print(f"  font:  {ui.sty('1', str(general.get('font')))}")
    try:
        context = load_context(project)
        results = render_all(project, context)
        compare_with_disk(project, results)
        stale = sum(1 for r in results if r.status != "unchanged")
        if context.unresolved:
            print(ui.sty("31", f"  {len(context.unresolved)} unresolved tokens (run `interdot check`)"))
        elif stale:
            print(ui.sty("33", f"  output is stale: {stale} of {len(results)} files would change (run `interdot generate`)"))
        else:
            print(ui.sty("32", f"  output is up to date ({len(results)} files)"))
    except (ConfigError, GenerationError) as exc:
        print(ui.sty("31", f"  broken: {exc}"))
        return 1
    ui.say("run `interdot --help` for commands")
    return 0


def cmd_generate(project: Project, args, ui: UI) -> int:
    context = load_context(project, theme=args.theme, font=args.font)
    if context.unresolved:
        for path, token in context.unresolved:
            ui.error(f"unresolved token {token} at {path}")
        ui.error(
            f"refusing to write broken configs; add the missing tokens to the "
            f"colorscheme or fix the theme config (theme={context.theme_name})"
        )
        return 1

    results = render_all(project, context)
    compare_with_disk(project, results)
    changed = [r for r in results if r.status != "unchanged"]

    if args.diff:
        diff = diff_results(project, results)
        if diff:
            print(diff)

    ui.say(f"theme {ui.sty('1', context.theme_name)} · font {ui.sty('1', context.font_name)}")
    _print_file_statuses(ui, results)

    if args.dry_run:
        ui.say(_summary(results) + " (dry run, nothing written)")
        return 0

    write_results(project, results)
    ui.say(_summary(results))

    hook_failures = 0
    hooks = _normalize_hooks(context.data.get("hooks"))
    if hooks and not args.no_hooks:
        if changed:
            hook_failures = _run_hooks(ui, project, hooks)
        else:
            ui.detail("no files changed; skipping hooks")
    return 1 if hook_failures else 0


def cmd_check(project: Project, args, ui: UI) -> int:
    themes = args.theme or None
    fonts = args.font or None
    reports = check_matrix(project, themes=themes, fonts=fonts)
    failed = [r for r in reports if not r.ok]

    for report in failed:
        print(ui.sty("31", f"✗ theme={report.theme} font={report.font}"))
        for error in report.errors:
            print(f"    {error}")

    warnings = check_project_warnings(project)
    for warning in warnings:
        ui.warn(warning)

    ok = len(reports) - len(failed)
    verdict = f"checked {len(reports)} theme/font combinations: {ok} ok, {len(failed)} failed"
    print(ui.sty("31" if failed else "32", verdict))
    return 1 if failed else 0


def cmd_list(project: Project, args, ui: UI) -> int:
    general = load_yaml(project.general_path) or {}
    active_theme, active_font = general.get("theme"), general.get("font")

    def section(title, names, active=None, tags=None):
        print(ui.sty("1", title))
        width = max((len(n) for n in names), default=0)
        for name in names:
            marker = "*" if name == active else " "
            line = f"  {marker} {name:<{width}}"
            if tags and tags.get(name):
                line += ui.sty("2", f"  [{tags[name]}]")
            print(ui.sty("32", line) if name == active else line)

    what = args.what
    if what in (None, "themes"):
        themes = available_themes(project)
        tags = {}
        for name in themes:
            config = load_yaml(project.themes_dir / f"{name}.yml") or {}
            parts = [p for p in (config.get("polarity"),
                                 f"⇄ {config['pair']}" if config.get("pair") else None) if p]
            tags[name] = ", ".join(parts)
        section("themes (* = active)", themes, active_theme, tags)
    if what in (None, "fonts"):
        section("fonts (* = active)", available_fonts(project), active_font)
    if what in (None, "colorschemes"):
        section("colorschemes", available_colorschemes(project))
    return 0


def cmd_preview(project: Project, args, ui: UI) -> int:
    if args.all:
        names = available_colorschemes(project)
    elif args.names:
        names = []
        for name in args.names:
            if name in available_colorschemes(project):
                names.append(name)
            elif name in available_themes(project):
                theme_config = load_yaml(project.themes_dir / f"{name}.yml") or {}
                names.append(theme_config.get("colorscheme", name))
            else:
                raise unknown_choice(
                    "colorscheme", name, available_colorschemes(project)
                )
    else:
        general = load_yaml(project.general_path) or {}
        theme_name = general.get("theme")
        if not theme_name:
            raise ConfigError("No active theme to preview; pass a name or set one in general.yml.")
        theme_config = load_yaml(project.themes_dir / f"{theme_name}.yml") or {}
        names = [theme_config.get("colorscheme", theme_name)]

    for i, name in enumerate(names):
        if i:
            print()
        print(render_palette(project, name, color=ui.color))
    return 0


def cmd_switch(project: Project, args, ui: UI) -> int:
    themes = available_themes(project)
    if args.name not in themes:
        raise unknown_choice("theme", args.name, themes)
    if args.font and args.font not in available_fonts(project):
        raise unknown_choice("font", args.font, available_fonts(project))

    text = project.general_path.read_text()
    new_text, n = re.subn(
        r"(?m)^theme:.*$", f'theme: "{args.name}"', text, count=1
    )
    if n == 0:
        raise ConfigError(
            f"Could not find a `theme:` line in {project.general_path}; edit it manually."
        )
    if args.font:
        new_text, n = re.subn(
            r"(?m)^font:.*$", f'font: "{args.font}"', new_text, count=1
        )
        if n == 0:
            raise ConfigError(
                f"Could not find a `font:` line in {project.general_path}; edit it manually."
            )
    project.general_path.write_text(new_text)
    ui.say(f"switched to theme {ui.sty('1', args.name)}"
           + (f", font {ui.sty('1', args.font)}" if args.font else ""))

    args.theme = args.font = None
    args.diff = args.dry_run = False
    return cmd_generate(project, args, ui)


def cmd_toggle(project: Project, args, ui: UI) -> int:
    """Jump to the active theme's light/dark counterpart (its `pair:`)."""
    general = load_yaml(project.general_path) or {}
    theme_name = general.get("theme")
    if not theme_name:
        raise ConfigError("No active theme to toggle; set `theme:` in general.yml first.")
    theme_config = load_yaml(project.themes_dir / f"{theme_name}.yml") or {}
    pair = theme_config.get("pair")
    if not pair:
        raise ConfigError(
            f"Theme {theme_name!r} has no `pair:` defined in its config, "
            "so there is nothing to toggle to."
        )
    args.name = pair
    args.font = None
    return cmd_switch(project, args, ui)


_LINK_STYLES = {
    "ok": ("2", "ok"),
    "created": ("32", "linked"),
    "retargeted": ("33", "retargeted"),
    "conflict": ("31", "conflict"),
    "missing-source": ("31", "missing source"),
}


def cmd_link(project: Project, args, ui: UI) -> int:
    general = load_yaml(project.general_path) or {}
    links = general.get("links")
    if not links:
        ui.say(
            "No links configured. Add a `links:` mapping to config/general.yml, e.g.\n"
            "  links:\n"
            '    ~/.tmux.conf: tmux/.tmux.conf\n'
            '    ~/.config/kitty/kitty.conf: kitty/kitty.conf'
        )
        return 0

    results = plan_links(project, links)
    if not args.dry_run:
        apply_links(results, force=args.force)

    failures = 0
    for result in results:
        code, label = _LINK_STYLES[result.status]
        if result.status in ("conflict", "missing-source"):
            failures += 1
        prefix = "would link" if args.dry_run and result.status != "ok" else label
        line = f"  {result.target} -> {result.source}  [{prefix}]"
        if result.detail:
            line += f"  ({result.detail})"
        print(ui.sty(code, line))
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    # Global options live on a shared parent applied to BOTH the top-level
    # parser and every subparser, so they work in either position
    # (`interdot -C DIR status` like git, or `interdot status -C DIR`).
    # SUPPRESS defaults mean an option omitted after the subcommand does not
    # clobber a value already parsed before it.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-C", "--directory", metavar="DIR", default=argparse.SUPPRESS,
                        help="project root (default: auto-detect)")
    common.add_argument("-q", "--quiet", action="store_true", default=argparse.SUPPRESS,
                        help="only print warnings and errors")
    common.add_argument("-v", "--verbose", action="store_true", default=argparse.SUPPRESS,
                        help="print extra detail")
    common.add_argument("--color", choices=["auto", "always", "never"], default=argparse.SUPPRESS,
                        help="when to use ANSI colors (default: auto)")

    parser = argparse.ArgumentParser(
        prog="interdot",
        description="Unified theme & font generator for dotfiles.",
        epilog=(
            "examples:\n"
            "  interdot                      show active theme and output freshness\n"
            "  interdot generate --diff      render everything, show what changed\n"
            "  interdot switch nord          set the theme and regenerate\n"
            "  interdot toggle               jump to the light/dark counterpart\n"
            "  interdot check                validate every theme x font combination\n"
            "  interdot preview --all        palette swatches for every colorscheme"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        color=True,
        suggest_on_error=True,
        parents=[common],
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", parents=[common],
                   help="show active theme/font and output freshness (default command)")

    p = sub.add_parser("generate", parents=[common],
                       help="render all templates into output/")
    p.add_argument("-t", "--theme", help="override the theme from general.yml")
    p.add_argument("-f", "--font", help="override the font from general.yml")
    p.add_argument("-n", "--dry-run", action="store_true",
                   help="show what would change without writing")
    p.add_argument("--diff", action="store_true",
                   help="print a unified diff of the changes")
    p.add_argument("--no-hooks", action="store_true",
                   help="skip the post-generate hooks from general.yml")

    p = sub.add_parser("check", parents=[common],
                       help="validate every theme/font combination renders cleanly")
    p.add_argument("-t", "--theme", action="append",
                   help="limit to this theme (repeatable)")
    p.add_argument("-f", "--font", action="append",
                   help="limit to this font (repeatable)")

    p = sub.add_parser("list", parents=[common],
                       help="list themes, fonts, and colorschemes")
    p.add_argument("what", nargs="?",
                   choices=["themes", "fonts", "colorschemes"],
                   help="section to list (default: all)")

    p = sub.add_parser("preview", parents=[common],
                       help="show palette swatches in the terminal")
    p.add_argument("names", nargs="*",
                   help="theme or colorscheme names (default: active theme)")
    p.add_argument("--all", action="store_true", help="preview every colorscheme")

    p = sub.add_parser("switch", parents=[common],
                       help="set the theme in general.yml and regenerate")
    p.add_argument("name", help="theme to switch to")
    p.add_argument("-f", "--font", help="also switch the font")
    p.add_argument("--no-hooks", action="store_true",
                   help="skip the post-generate hooks from general.yml")

    p = sub.add_parser("toggle", parents=[common],
                       help="switch to the active theme's light/dark pair")
    p.add_argument("--no-hooks", action="store_true",
                   help="skip the post-generate hooks from general.yml")

    p = sub.add_parser("link", parents=[common],
                       help="symlink dotfile locations to generated output")
    p.add_argument("-n", "--dry-run", action="store_true",
                   help="show what would happen without touching anything")
    p.add_argument("--force", action="store_true",
                   help="back up and replace real files that are in the way")

    return parser


_HANDLERS = {
    "status": cmd_status,
    "generate": cmd_generate,
    "check": cmd_check,
    "list": cmd_list,
    "preview": cmd_preview,
    "switch": cmd_switch,
    "toggle": cmd_toggle,
    "link": cmd_link,
}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in COMMANDS and not argv[0].startswith("-"):
        import difflib

        ui = UI()
        ui.error(f"unknown command {argv[0]!r}")
        close = difflib.get_close_matches(argv[0], COMMANDS, n=1)
        if close:
            print(f"did you mean: interdot {close[0]}", file=sys.stderr)
        print(f"commands: {', '.join(COMMANDS)}", file=sys.stderr)
        return 2
    if not argv:
        argv = ["status"]

    args = build_parser().parse_args(argv)
    if getattr(args, "command", None) is None:
        args.command = "status"
    # Global options use SUPPRESS defaults so position doesn't clobber them,
    # which means an omitted flag has no attribute at all.
    directory = getattr(args, "directory", None)
    ui = UI(
        quiet=getattr(args, "quiet", False),
        verbose=getattr(args, "verbose", False),
        color=getattr(args, "color", "auto"),
    )
    try:
        if directory:
            project = Project.locate(Path(directory), fallback=False)
        else:
            project = Project.locate(Path.cwd())
        ui.detail(f"project root: {project.root}")
        return _HANDLERS[args.command](project, args, ui)
    except (ConfigError, GenerationError) as exc:
        ui.error(str(exc))
        return 1
    except KeyboardInterrupt:
        return 130
