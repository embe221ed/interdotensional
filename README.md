# interd•tensional

One palette, every tool. A Python-powered dotfile generator that maintains a
unified theme across development tools: pick a theme and font once, and
generate consistent configs for Neovim, Kitty, Ghostty, Tmux, Zsh, Zellij,
IPython, fzf, and colorls.

## Quickstart

```bash
git clone https://github.com/embe221ed/interdotensional.git
cd interdotensional
uv sync

uv run interdot                 # status: active theme/font, is output fresh?
uv run interdot generate       # render everything into output/
uv run interdot switch nord    # change theme and regenerate in one step
```

`python generate.py` still works as an alias for `interdot generate`.

## Commands

| Command | What it does |
|---------|--------------|
| `interdot` / `interdot status` | Active theme/font and whether `output/` is stale |
| `interdot generate` | Render all templates into `output/` (only rewrites changed files) |
| `interdot generate -n --diff` | Dry run with a unified diff of what would change |
| `interdot generate -t nord` | One-off render with a different theme (doesn't touch general.yml) |
| `interdot switch <theme>` | Set the theme in `general.yml`, regenerate, run hooks |
| `interdot toggle` | Jump to the active theme's light/dark counterpart |
| `interdot check` | Validate **every** theme × font combination renders cleanly |
| `interdot list` | Themes, fonts, and colorschemes, with the active ones marked |
| `interdot preview [name \| --all]` | Truecolor palette swatches in the terminal |
| `interdot link [-n] [--force]` | Symlink dotfile locations to generated output |

Exit codes: `0` success, `1` config/render/check failure, `2` usage error.
Colors respect `NO_COLOR` and `--color=auto|always|never`.

## How it works

Each theme is defined by two files:

- **Colorscheme** (`colorschemes/{name}.yml`) — the raw palette: flat map of
  token name → hex value. The single source of truth for colors.
- **Theme config** (`config/themes/{name}.yml`) — per-tool settings that
  reference palette colors via `$token$` substitution (`$red$`,
  `$bg_primary$`, …).

Token substitution happens before Jinja2 rendering, so templates receive
fully resolved hex values. Rendering is **strict**: an unresolved token or a
missing variable fails loudly instead of writing a silently broken config.

Templates are auto-discovered: every `templates/<tool>/<name>.j2` renders to
`output/<tool>/<name>`. Adding a tool = dropping in one template file and
adding a `tools.<name>` section to the theme configs — no code changes.

Writes are atomic, and unchanged files are never rewritten (mtimes stay
put, so file watchers don't spuriously reload).

### Theme pairing (light/dark)

Theme configs may declare `polarity: light|dark` and `pair: <theme>`.
`interdot toggle` flips between the pair — day/night switching in one
command.

### Hooks

Add a `hooks:` list to `config/general.yml` to make a theme switch apply
live. Hooks run after a generate that changed at least one file
(skip with `--no-hooks`):

```yaml
hooks:
  - "tmux source-file ~/.tmux.conf"
  - "kill -SIGUSR1 $(pgrep kitty) 2>/dev/null || true"
```

### Links

Declare where the generated files should be symlinked, then run
`interdot link` (dry-run with `-n`; real files in the way are only replaced
with `--force`, which backs them up to `*.bak`):

```yaml
links:
  ~/.tmux.conf: tmux/.tmux.conf
  ~/.config/kitty/kitty.conf: kitty/kitty.conf
```

### Color math in templates

Templates can derive shades instead of palettes hand-maintaining every
variant:

```jinja
background {{ theme.colors.bg_primary | darken(10) }}
border     {{ theme.colors.blue | mix(theme.colors.bg_primary, 40) }}
fg         {{ theme.colors.fg_primary | strip_hash }}
```

Available filters: `lighten(pct)`, `darken(pct)`, `mix(color, pct)`,
`strip_hash`.

## Project structure

```
interdotensional/
├── colorschemes/            # color palettes (token → hex)
├── config/
│   ├── general.yml          # active theme/font, UI settings, hooks, links
│   ├── themes/{name}.yml    # per-theme tool configurations ($token$ refs)
│   └── fonts/{name}.yml     # font configurations
├── templates/{tool}/*.j2    # Jinja2 templates (auto-discovered)
├── output/{tool}/*          # generated files (gitignored)
├── interdotensional/        # the package: config, tokens, generate, check,
│                            #   preview, links, filters, cli
├── tests/                   # pytest suite (see below)
├── docs/                    # theme-building walkthroughs
└── generate.py              # legacy shim → interdot generate
```

## Themes

| Theme | Polarity | Pair |
|-------|----------|------|
| catppuccin-frappe | dark | catppuccin-latte |
| catppuccin-latte | light | catppuccin-frappe |
| gruvbox-material-dark | dark | gruvbox-material-light |
| gruvbox-material-light | light | gruvbox-material-dark |
| nord | dark | – |
| onedarkpro-onedark | dark | – |
| tokyonight-storm | dark | tokyonight-day |
| tokyonight-day | light | tokyonight-storm |

Fonts: `jetbrains-mono`, `maple-mono`, `monaspace-argon`.

## Adding a new theme

1. Create `colorschemes/{name}.yml` with your palette
2. Create `config/themes/{name}.yml` with per-tool settings using `$token$`
   references (copy a complete theme like `catppuccin-frappe` as a start)
3. Run `uv run interdot check -t {name}` — it renders the theme against every
   font and reports every missing token or section at once
4. `uv run interdot preview {name}` to eyeball the palette
5. `uv run interdot switch {name}`

See `docs/gruvbox-material-dark.md` for a detailed walkthrough.

## Development

```bash
uv sync                  # installs the package + dev deps (pytest)
uv run pytest -q         # full suite, ~2s, no network
uv run interdot check    # the same validation the matrix test enforces
```

The test suite covers the token/substitution utilities, config loading and
error messages, the render/write/diff lifecycle, links, color filters, the
CLI (in-process, no subprocesses), and a parametrized matrix test asserting
every theme × font combination renders with zero errors.

## License

MIT
