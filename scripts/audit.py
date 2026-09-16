#!/usr/bin/env python
"""Read-only contrast and contract audit of one or more themes.

Every text/background pair the templates draw is checked against a floor of
min(WCAG target, the ratio the gruvbox theme of the same polarity gets for the
same pair) - "at least as readable as the reference theme, pair by pair".
NEVER writes into the repo (no generate/switch/link).

usage:  uv run python scripts/audit.py [theme ...]        (default: every theme)
        uv run python scripts/audit.py -v nord             (every row, not only LOW)
        uv run python scripts/audit.py --json nord         (machine-readable)
        uv run python scripts/audit.py --near '#d4967e'    (nearest xterm-256 index)

Sections per theme:
  tokens     contract tokens missing from the colorscheme
  shape      tools.* keys missing/extra vs config/themes/gruvbox-material-dark.yml
  nvim       catppuccin_overrides key set + fields validity
  contrast   WCAG ratios for every text/background pair the templates draw
  clock      what tmux.clock resolves to, and the nearest index for the accents
"""
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
from interdotensional.config import Project, available_themes, load_context, load_yaml  # noqa: E402
from interdotensional.filters import darken, mix  # noqa: E402

PROJECT = Project(root=_ROOT)
REF = "gruvbox-material-dark"

# --- the gruvbox contract -----------------------------------------------------
CONTRACT_TOKENS = [
    # accents
    "red", "orange", "yellow", "green", "aqua", "blue", "purple",
    "pink", "peach", "terracotta", "maroon",
    # text ladder
    "fg_primary", "fg_secondary", "fg_muted", "fg_dim", "fg_faint",
    # surfaces
    "border", "panel_raised", "panel", "panel_inset",
    "bg_primary", "bg_deep", "bg_abyss",
    # greys + leaf ladder aliases
    "grey0", "grey1", "grey2", "fg0", "fg1",
]
CATPPUCCIN_KEYS = [
    "rosewater", "flamingo", "pink", "mauve", "red", "maroon", "peach", "yellow",
    "green", "teal", "sky", "sapphire", "blue", "lavender", "text", "subtext1",
    "subtext0", "overlay2", "overlay1", "overlay0", "surface2", "surface1",
    "surface0", "base", "mantle", "crust",
]
TOKYONIGHT_KEYS = {
    "bg", "bg_dark", "bg_dark1", "bg_highlight", "blue", "blue0", "blue1", "blue2",
    "blue5", "blue6", "blue7", "comment", "cyan", "dark3", "dark5", "fg", "fg_dark",
    "fg_gutter", "green", "green1", "green2", "magenta", "magenta2", "orange",
    "purple", "red", "red1", "teal", "terminal_black", "yellow", "black",
    "border_highlight", "border", "bg_visual", "bg_search", "bg_statusline",
    "bg_sidebar", "bg_float", "bg_popup", "fg_sidebar", "fg_float", "none",
}


# --- colour math --------------------------------------------------------------
def rgb(h):
    h = str(h).strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def is_hex(v):
    v = str(v).strip()
    return v.startswith("#") and len(v) == 7 and all(c in "0123456789abcdefABCDEF" for c in v[1:])


def luminance(h):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def xterm256_table():
    table = {}
    system = ["#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
              "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff"]
    for i, h in enumerate(system):
        table[i] = tuple(int(h[j:j + 2], 16) for j in (1, 3, 5))
    levels = [0, 95, 135, 175, 215, 255]
    for i in range(216):
        r, g, b = levels[i // 36], levels[(i // 6) % 6], levels[i % 6]
        table[16 + i] = (r, g, b)
    for i in range(24):
        v = 8 + i * 10
        table[232 + i] = (v, v, v)
    return table


XT = xterm256_table()


def nearest_index(h):
    r, g, b = rgb(h)
    best = min(XT, key=lambda i: (XT[i][0] - r) ** 2 + (XT[i][1] - g) ** 2 + (XT[i][2] - b) ** 2)
    return best, "#%02x%02x%02x" % XT[best]


def index_hex(i):
    i = int(i)
    return "#%02x%02x%02x" % XT[i] if i in XT else "?"


# --- checks -------------------------------------------------------------------
def shape(d, prefix=""):
    """Flatten a nested mapping into dotted key paths (values ignored)."""
    out = set()
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                sub = shape(v, p)
                out |= sub if sub else {p}
            else:
                out.add(p)
    return out


def audit(theme):
    ctx = load_context(PROJECT, theme=theme)
    t = ctx.data["theme"]
    colors = t["colors"]
    tools = t["tools"]
    report = {"theme": theme, "polarity": t.get("polarity"), "pair": t.get("pair"),
              "colorscheme": t.get("colorscheme", theme),
              "unresolved": ctx.unresolved, "problems": [], "info": []}

    # tokens
    missing = [k for k in CONTRACT_TOKENS if k not in colors]
    if missing:
        report["problems"].append(f"colorscheme lacks contract tokens: {missing}")
    non_hex = [k for k, v in colors.items() if not isinstance(v, dict) and not is_hex(v)]
    if non_hex:
        report["problems"].append(f"non-hex palette values: {non_hex}")

    # shape vs reference
    ref = load_yaml(PROJECT.themes_dir / f"{REF}.yml")["tools"]
    ref_shape = shape(ref, "tools")
    my_shape = shape(tools, "tools")
    # text_darken maps are polarity-specific: ignore their leaves
    # kitty is `kitty:` (empty) in gruvbox and `kitty: {name: ...}` where a theme file exists - both allowed
    strip = lambda s: {p for p in s if ".text_darken." not in p and not p.startswith("tools.nvim.catppuccin_overrides.")
                       and not p.startswith("tools.kitty")}
    ref_s, my_s = strip(ref_shape), strip(my_shape)
    if ref_s - my_s:
        report["problems"].append(f"missing vs {REF}: {sorted(ref_s - my_s)}")
    if my_s - ref_s:
        report["info"].append(f"extra vs {REF}: {sorted(my_s - ref_s)}")

    # nvim
    nvim = tools.get("nvim", {})
    ov = nvim.get("catppuccin_overrides")
    if nvim.get("colorscheme") == "catppuccin":
        if ov is None:
            report["problems"].append("nvim: catppuccin engine without catppuccin_overrides")
        else:
            if list(ov.keys()) != CATPPUCCIN_KEYS:
                report["problems"].append(
                    f"nvim: catppuccin_overrides keys differ from the 26 catppuccin keys: "
                    f"missing={sorted(set(CATPPUCCIN_KEYS) - set(ov))} extra={sorted(set(ov) - set(CATPPUCCIN_KEYS))}")
            bad = {k: v for k, v in ov.items() if not is_hex(v)}
            if bad:
                report["problems"].append(f"nvim: non-hex override values {bad}")
            if nvim.get("scheme") != "gruvbox-material":
                report["info"].append(f"nvim: scheme={nvim.get('scheme')!r} (overrides are only read by scheme 'gruvbox-material')")
        for k, v in nvim.get("fields", {}).items():
            if v != "NONE" and v not in CATPPUCCIN_KEYS:
                report["problems"].append(f"nvim.fields.{k}={v!r} is not a catppuccin palette key")
    elif nvim.get("colorscheme") == "tokyonight":
        for k, v in nvim.get("fields", {}).items():
            if v != "NONE" and v not in TOKYONIGHT_KEYS:
                report["problems"].append(f"nvim.fields.{k}={v!r} is not a tokyonight palette key")
    # 256-color leaks in tools that need hex
    for sec in ("zsh",):
        for k, v in tools.get(sec, {}).get("colors", {}).items():
            if not is_hex(v):
                report["problems"].append(f"tools.{sec}.colors.{k}={v!r} is not hex (gruvbox uses palette hex)")
    for k, v in tools.get("colorls", {}).items():
        if not is_hex(v):
            report["problems"].append(f"tools.colorls.{k}={v!r} is not hex (gruvbox uses palette hex)")
    for k, v in tools.get("interdimux", {}).items():
        if not is_hex(v):
            report["problems"].append(f"tools.interdimux.{k}={v!r} is not hex")

    # --- contrast pairs -------------------------------------------------------
    pairs = []  # (group, label, fg, bg, minimum)

    def add(group, label, fg, bg, minimum):
        pairs.append((group, label, fg, bg, minimum))

    bg = colors.get("bg_primary")
    # leaf
    leaf = tools.get("leaf")
    if leaf:
        c = leaf["colors"]
        td = leaf.get("text_darken", {}) or {}
        accent_fg = darken(c["accent"], td.get("accent", 0))
        accent2_fg = darken(c["accent2"], td.get("accent2", 0))
        warning_fg = darken(c["warning"], td.get("warning", 0))
        strong_fg = darken(c["fg_strong"], td.get("strong", 0))
        success_fg = darken(c["success"], td.get("success", 0))
        watch_bg = mix(c["success"], c["bg_deep"], 85)
        error_bg = mix(c["danger"], c["bg_deep"], 85)
        mark_bg = mix(c["accent"], c["bg"], 60)
        L = "leaf"
        add(L, "body fg on bg", c["fg"], c["bg"], 4.5)
        add(L, "strong on bg", strong_fg, c["bg"], 4.5)
        add(L, "H1/table header/ol marker: accent_fg on bg", accent_fg, c["bg"], 4.5)
        add(L, "H2/tips/list1: success_fg on bg", success_fg, c["bg"], 4.5)
        add(L, "H3/links/notes: info on bg", c["info"], c["bg"], 4.5)
        add(L, "H4/latex/important: special on bg", c["special"], c["bg"], 4.5)
        add(L, "H5+/mermaid kw: accent2_fg on bg", accent2_fg, c["bg"], 4.5)
        add(L, "inline code: accent2_fg on panel", accent2_fg, c["panel"], 4.5)
        add(L, "latex inline: special on panel", c["special"], c["panel"], 4.5)
        add(L, "alert warning: warning_fg on bg", warning_fg, c["bg"], 4.5)
        add(L, "alert caution: danger on bg", c["danger"], c["bg"], 4.5)
        add(L, "code label/blockquote/task: dim on bg", c["dim"], c["bg"], 3.0)
        add(L, "mark: strong_fg on mark_bg", strong_fg, mark_bg, 4.5)
        add(L, "status brand: bg on accent_fg", c["bg"], accent_fg, 4.5)
        add(L, "status filename: strong_fg on panel", strong_fg, c["panel"], 4.5)
        add(L, "status search: accent_fg on panel", accent_fg, c["panel"], 4.5)
        add(L, "status watch/success: success_fg on tinted", success_fg, watch_bg, 4.5)
        add(L, "status reloaded: bg on success", c["bg"], c["success"], 4.5)
        add(L, "status warning: warning_fg on bg_deep", warning_fg, c["bg_deep"], 4.5)
        add(L, "status error: danger on tinted", c["danger"], error_bg, 4.5)
        add(L, "status percent: accent_fg on bg_deep", accent_fg, c["bg_deep"], 4.5)
        add(L, "chrome text: dim on bg_deep", c["dim"], c["bg_deep"], 3.0)
        add(L, "toc accent: accent2_fg on bg_deep", accent2_fg, c["bg_deep"], 4.5)
        add(L, "toc active: strong_fg on panel", strong_fg, c["panel"], 4.5)
        add(L, "toc active secondary: fg on panel", c["fg"], c["panel"], 4.5)
        add(L, "toc inactive: muted on bg_deep", c["muted"], c["bg_deep"], 4.5)
        add(L, "toc index/secondary inactive: faint on bg_deep", c["faint"], c["bg_deep"], 1.5)
        add(L, "search highlight: fg on faint", c["fg"], c["faint"], 3.0)
        add(L, "rule/border line on bg", c["border"], c["bg"], 1.3)
        add(L, "code frame/table line: faint on bg", c["faint"], c["bg"], 1.3)
        add(L, "panel chip visible on bg", c["panel"], c["bg"], 1.1)
        add(L, "chrome bg_deep visible on bg", c["bg_deep"], c["bg"], 1.05)

    # web (the same roles, stricter: both bg and bg_deep, with the web map)
    if leaf:
        c = leaf["colors"]
        web = tools.get("web", {}) or {}
        td = web.get("text_darken", leaf.get("text_darken", {}) or {}) or {}
        W = "web"
        for role in ("fg", "fg_strong", "muted", "accent", "accent2", "success", "info", "special", "warning", "danger"):
            v = darken(c[role], td.get(role, 0))
            add(W, f"{role} on bg", v, c["bg"], 4.5)
            add(W, f"{role} on bg_deep", v, c["bg_deep"], 4.5)
        add(W, "dim on bg", darken(c["dim"], td.get("dim", 0)), c["bg"], 3.0)
        tm = tools["tmux"]["colors"]
        add(W, "pane_active (title text) on bg", darken(tm["pink"], td.get("pane_active", 0)), c["bg"], 4.5)
        add(W, "pane_border line on bg", tm["dim"], c["bg"], 3.0)
        add(W, "select_fg on select_bg", darken(tm["selected"]["fg"], td.get("select_fg", 0)), tm["selected"]["bg"], 4.5)
        add(W, "prompt_dir on bg", darken(web.get("prompt_dir", c["info"]), td.get("prompt_dir", 0)), c["bg"], 4.5)

    # tmux
    tm = tools["tmux"]["colors"]
    T = "tmux"
    add(T, "status text: dim on bg", tm["dim"], bg, 3.0)
    add(T, "active window/accent: pink on bg", tm["pink"], bg, 4.5)
    add(T, "prefix/zoom flag: yellow on bg", tm["yellow"], bg, 4.5)
    add(T, "menu/mode/message: selected.fg on selected.bg", tm["selected"]["fg"], tm["selected"]["bg"], 4.5)
    add(T, "selected.bg visible on bg", tm["selected"]["bg"], bg, 1.1)
    add(T, "copy match: selected.bg text on yellow", tm["selected"]["bg"], tm["yellow"], 4.5)
    add(T, "copy current match: selected.bg text on pink", tm["selected"]["bg"], tm["pink"], 4.5)
    add(T, "nested-off status: dim on selected.bg", tm["dim"], tm["selected"]["bg"], 3.0)

    # interdimux
    im = tools.get("interdimux")
    if im:
        I = "interdimux"
        for k in ("accent", "path", "git", "ssh", "editor", "success", "danger", "query"):
            add(I, f"{k} on bg", im[k], bg, 4.5)
        add(I, "header on bg", im["header"], bg, 3.0)
        add(I, "match_current on current_bg", im["match_current"], im["current_bg"], 4.5)
        add(I, "query on current_bg", im["query"], im["current_bg"], 4.5)
        add(I, "current_bg visible on bg", im["current_bg"], bg, 1.1)
        add(I, "tree glyphs on bg", im["tree"], bg, 1.5)
        add(I, "separator/border line on bg", im["separator"], bg, 1.3)
        add(I, "menu_sel_fg on accent", im["menu_sel_fg"], im["accent"], 4.5)

    # zsh
    zc = tools["zsh"]["colors"]
    Z = "zsh"
    for k, v in zc.items():
        if is_hex(v):
            add(Z, f"{k} on bg", v, bg, 3.0 if k == "comment" else 4.5)

    # fzf
    fz = tools["fzf"]
    F = "fzf"
    add(F, "fg on bg", fz["fg"], bg, 4.5)
    add(F, "fg on selected_bg", fz["fg"], fz["selected_bg"], 4.5)
    add(F, "hl on bg", fz["hl"], bg, 4.5)
    add(F, "hl on selected_bg", fz["hl"], fz["selected_bg"], 4.5)
    for k in ("info", "prompt", "pointer", "marker", "spinner", "label"):
        add(F, f"{k} on bg", fz[k], bg, 4.5)
    add(F, "header/disabled on bg", fz["header"], bg, 3.0)
    add(F, "selected_bg visible on bg", fz["selected_bg"], bg, 1.1)
    add(F, "border on bg", fz["border"], bg, 1.5)
    add(F, "separator/scrollbar on bg", fz["separator"], bg, 1.3)

    # colorls
    cl = tools["colorls"]
    C = "colorls"
    for k, v in cl.items():
        if is_hex(v):
            add(C, f"{k} on bg", v, bg, 3.0 if k in ("tree", "no_modifier", "no_access") else 4.5)

    rows = []
    ref_name = "gruvbox-material-light" if t.get("polarity") == "light" else "gruvbox-material-dark"
    ref_rows = {} if theme == ref_name else {
        (r["group"], r["label"]): r["ratio"] for r in audit(ref_name)["contrast"]}
    for group, label, fg, bg_, minimum in pairs:
        try:
            r = contrast(fg, bg_)
        except Exception as exc:  # non-hex
            rows.append({"group": group, "label": label, "fg": fg, "bg": bg_, "ratio": None, "min": minimum, "ref": None, "floor": minimum, "ok": False, "err": str(exc)})
            continue
        ref = ref_rows.get((group, label))
        floor = minimum if ref is None else min(minimum, ref)
        rows.append({"group": group, "label": label, "fg": fg, "bg": bg_, "ratio": round(r, 2), "min": minimum,
                     "ref": ref, "floor": round(floor, 2), "ok": r + 0.05 >= floor})
    report["contrast"] = rows
    report["reference"] = ref_name

    # clock
    clock = tools["tmux"].get("clock")
    report["clock"] = {
        "index": clock, "resolves_to": index_hex(clock) if clock is not None else None,
        "nearest_pink": nearest_index(tm["pink"]), "nearest_yellow": nearest_index(tm["yellow"]),
        "nearest_orange": nearest_index(colors["orange"]) if "orange" in colors else None,
    }
    return report


def print_report(rep, verbose=False):
    print(f"=== {rep['theme']}  [{rep['polarity']}, pair={rep['pair']}, colorscheme={rep['colorscheme']}]")
    for u in rep["unresolved"]:
        print(f"  UNRESOLVED {u}")
    for p in rep["problems"]:
        print(f"  PROBLEM  {p}")
    for i in rep["info"]:
        print(f"  info     {i}")
    fails = [r for r in rep["contrast"] if not r["ok"]]
    print(f"  contrast: {len(rep['contrast']) - len(fails)}/{len(rep['contrast'])} pairs at or above the floor "
          f"(floor = min(WCAG target, the same pair in {rep['reference']}))")
    for r in (rep["contrast"] if verbose else fails):
        flag = "ok " if r["ok"] else "LOW"
        ref = f"ref {r['ref']}" if r.get("ref") is not None else "no ref"
        print(f"    {flag} {r['group']:<10} {r['label']:<48} {r['fg']} on {r['bg']}  {r['ratio']}  (target {r['min']}, {ref}, floor {r['floor']})")
    ck = rep["clock"]
    print(f"  clock: colour{ck['index']} = {ck['resolves_to']}; nearest pink {ck['nearest_pink']}, yellow {ck['nearest_yellow']}, orange {ck['nearest_orange']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--near":
        for h in args[1:]:
            print(h, "->", nearest_index(h))
        sys.exit(0)
    as_json = "--json" in args
    verbose = "-v" in args
    names = [a for a in args if not a.startswith("-")] or available_themes(PROJECT)
    reports = [audit(n) for n in names]
    if as_json:
        print(json.dumps(reports, indent=1))
    else:
        for rep in reports:
            print_report(rep, verbose)
            print()
