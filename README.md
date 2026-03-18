# interd•tensional

A Python-powered dotfile generator that maintains a unified theme across development tools. Uses centralized YAML configuration and Jinja2 templating to produce config files for Neovim, Kitty, Ghostty, Tmux, Zsh, Zellij, IPython, and colorls.

## How it works

1. Pick a theme and font in `config/general.yml`
2. Run `python generate.py`
3. Symlink or copy from `output/` to your dotfile locations

Each theme is defined by two files:
- **Colorscheme** (`colorschemes/{name}.yml`) — the raw color palette (hex values)
- **Theme config** (`config/themes/{name}.yml`) — tool-specific settings that reference palette colors via `$token$` substitution

Token substitution (`$red$`, `$bg_primary$`, etc.) happens before Jinja2 rendering, so templates receive fully resolved hex values.

## Project structure

```
interdotensional/
├── colorschemes/              # color palettes (hex values)
│   ├── catppuccin-frappe.yml
│   ├── catppuccin-latte.yml
│   ├── gruvbox-material-dark.yml
│   ├── nord.yml
│   ├── onedarkpro-onedark.yml
│   ├── tokyonight-day.yml
│   └── tokyonight-storm.yml
├── config/
│   ├── general.yml            # active theme, font, UI settings
│   ├── themes/                # per-theme tool configurations
│   │   └── {name}.yml
│   └── fonts/                 # font configurations
│       ├── jetbrains-mono.yml
│       ├── maple-mono.yml
│       └── monaspace-argon.yml
├── templates/                 # Jinja2 templates
│   ├── colorls/
│   ├── ghostty/
│   ├── ipython/
│   ├── kitty/
│   ├── nvim/
│   ├── tmux/
│   ├── zellij/
│   └── zsh/
├── output/                    # generated config files
├── docs/                      # theme documentation
├── lib/                       # token substitution utilities
├── generate.py                # main generation script
└── requirements.txt           # jinja2, pyyaml
```

## Themes

| Theme | Type | Status |
|-------|------|--------|
| catppuccin-frappe | Dark | Complete — reference theme |
| catppuccin-latte | Light | Complete |
| gruvbox-material-dark | Dark | Complete — custom gruvbox + Claude palette |
| nord | Dark | Base support |
| onedarkpro-onedark | Dark | Base support |
| tokyonight-storm | Dark | Base support |
| tokyonight-day | Light | Base support |

## Supported tools

| Tool | Template | Notes |
|------|----------|-------|
| Neovim | `nvim/globals.lua.j2`, `nvim/colors.lua.j2` | Colorscheme config + semantic color mapping |
| Ghostty | `ghostty/config.j2` | Terminal theme selection, font settings |
| Kitty | `kitty/kitty.conf.j2` | Full terminal config |
| Tmux | `tmux/tmux.conf.j2`, `tmux/theme.sh.j2` | Config + powerline theme |
| Zsh | `zsh/theme.zsh-theme.j2` | Prompt theme (ANSI 256 colors) |
| Zellij | `zellij/config.kdl.j2` | Terminal multiplexer config |
| IPython | `ipython/ipython_config.py.j2` | REPL configuration |
| colorls | `colorls/dark_colors.yaml.j2` | File listing colors (hex or CSS names) |

## Installation

```bash
git clone https://github.com/embe221ed/interdotensional.git
cd interdotensional
pip install -r requirements.txt
```

## Usage

```bash
# edit config/general.yml to select theme and font
python generate.py
# deploy: symlink output files to their target locations
```

## Adding a new theme

1. Create `colorschemes/{name}.yml` with your color palette
2. Create `config/themes/{name}.yml` with tool-specific settings using `$token$` references
3. Set `theme: "{name}"` in `config/general.yml`
4. Run `python generate.py`

See `docs/gruvbox-material-dark.md` for a detailed example of building a custom theme.

## License

MIT
