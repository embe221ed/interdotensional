# The theme contract

`gruvbox-material-dark` and `gruvbox-material-light` are the reference themes.
Every other theme fills the same palette vocabulary and carries the same tool
sections, so switching themes never changes *what* is themed — only the
colours. `tests/test_contract.py` enforces it; `interdot check` still catches
the rendering side.

## Palette vocabulary (28 tokens)

A colorscheme may keep its upstream names (catppuccin's `rosewater…crust`,
nord's `origin…artic_ocean`, tokyonight's `bg_dark…magenta2`) as extra tokens;
YAML anchors keep one hex per colour (`teal: &teal "#81c8be"`, `aqua: *teal`).
When an upstream name collides with a contract token but must keep a different
value (latte's pastel `pink` for the editor versus the ink `pink` the terminal
draws), nest the upstream palette under a map — catppuccin uses `ctp:` — and
reference it as `$ctp.pink$` from the one consumer that needs it. Every
colorscheme's ratios and derivations are spelled out in its family doc
(`docs/catppuccin.md`, `docs/nord.md`, `docs/onedarkpro.md`, `docs/tokyonight.md`).

### Accents

| token | role | fed into |
|---|---|---|
| `red` | errors, danger | interdimux danger · leaf danger · zsh failed ❯ / ✘ · colorls dead_link/error/deletion · nvim red |
| `orange` | the warm secondary accent | tmux selection text · fzf match + prompt · interdimux accent · leaf accent2 · colorls dir · nvim peach (numbers) |
| `yellow` | types, search, modifications; leaf brand | tmux prefix/zoom flags · fzf marker · interdimux path · leaf accent + warning · zsh dirty ✗ / venv / vi · colorls file_medium · nvim yellow |
| `green` | strings, success | interdimux editor + success · leaf success · zsh prompt ❯ · colorls executable · nvim green |
| `aqua` | constants, links, the cwd colour | zsh cwd · web prompt_dir · colorls recognized_file/link · nvim teal + sapphire |
| `blue` | identifiers, info | fzf info · interdimux ssh · leaf info · colorls unrecognized_file/user · nvim blue + sky |
| `purple` | numbers, git, special | fzf spinner · interdimux git · leaf special · colorls read/day_old · nvim mauve (keywords) |
| `pink` | **the UI accent** — everything that says "active" | tmux active border, status ❯, menu/popup border, current match · fzf border · zsh branch · colorls exec · nvim rosewater/pink + `accent` (CursorLineNr, TabLineSel, lualine a, bufferline selected) |
| `peach` | mid warm | colorls hour_old |
| `terracotta` | brand primary, the most saturated warm | fzf pointer · nvim flamingo |
| `maroon` | soft rose | nvim maroon (function parameters) |

Each family keeps its own identity for `pink`: catppuccin pink, nord purple,
One Dark purple, tokyonight magenta2, gruvbox soft terracotta.

### Text ladder

`fg_primary` is the strongest body text; every step down is quieter. On a
light theme "quieter" means lighter, so `fg_secondary` is the emphasis colour
there (gruvbox-light: primary `#654735`, secondary `#4f3829`).

| token | fed into |
|---|---|
| `fg_primary` | fzf fg + query · interdimux query · colorls report · nvim text |
| `fg_secondary` | fzf label · colorls normal · nvim subtext1 + lavender |
| `fg_muted` | leaf muted (inactive TOC) · colorls file_small |
| `fg_dim` | tmux status text + inactive borders · fzf header · interdimux header · colorls no_access · nvim overlay2 |
| `fg_faint` | interdimux tree · zsh comments · colorls tree/no_modifier · leaf faint lines · nvim overlay1 |
| `fg0` / `fg1` | leaf body / leaf emphasis (`fg1` always has more contrast than `fg0`) |
| `grey0` `grey1` `grey2` | neutral greys, polarity-independent; `grey1` is leaf chrome text, zsh git punctuation, nvim subtext0 |

### Surfaces

| token | fed into |
|---|---|
| `bg_primary` | **the terminal background** — equals the ghostty theme's `background` · leaf bg · nvim base · interdimux menu_sel_fg |
| `bg_deep` | leaf TOC/status chrome · nvim mantle (NvimTree, Noice) |
| `bg_abyss` | nvim crust (Telescope, NoicePopup) |
| `panel_inset` | tmux selection/menu/popup background · interdimux current row · nvim surface0 |
| `panel` | fzf selected row · leaf chips (badges, inline code, active TOC row) · nvim surface1 |
| `panel_raised` | nvim surface2 (PmenuSel, FloatTitle, bufferline separators) |
| `border` | fzf separator · interdimux separator/border · leaf rules · nvim overlay0 (NonText, fold column, and through `fields.comment` the `vim.g.colors.comment` chrome roles); editor comments themselves are `overlay2` = `fg_dim` |

Ordering. Dark: `bg_abyss < bg_deep < bg_primary < panel_inset < panel <
panel_raised < border` in lightness. Light: `bg_primary` is the lightest and
everything else steps *down* from it — `bg_deep`, `bg_abyss` on the chrome
side, `panel_inset < panel < panel_raised < border` on the raised side.

## Theme config shape

Copy the gruvbox config of the same polarity. The only lines that legitimately
differ between themes:

- `name`, `polarity`, `pair` (both directions)
- `tools.tmux.clock` — an xterm-256 index near the theme's warm accent
- `tools.ipython.pygments_style` — an installed Pygments style of the right polarity
- `tools.ghostty.name` — a bundled ghostty theme whose `background` equals `bg_primary`
- `tools.kitty.name` — only when a differently named file exists in `dotfiles/kitty/`
- `tools.leaf.accent` / `accent2` and any commented per-theme leaf deviation
- `tools.leaf.syntax` (`base16-ocean.dark` / `.light`)
- `text_darken` maps — light themes only, tuned so leaf chips and the web's
  4.5:1 both hold (see below)
- `tools.nvim.theme` (flavour) and, for a native-plugin theme, its `fields`

Everything else — zsh roles, colorls mapping, fzf keys, interdimux keys, web
`prompt_dir`, the leaf surface/text roles — is the gruvbox line verbatim.

## Neovim engines

- **catppuccin-with-overrides** (`colorscheme: catppuccin`, `scheme:
  gruvbox-material`): the renderer gruvbox introduced. catppuccin.nvim is
  loaded for its 69 integrations and its whole palette is replaced by the 26
  `catppuccin_overrides` derived from the colorscheme, so Telescope, NvimTree,
  blink, noice, gitsigns and the user's custom highlights are painted from the
  same tokens as tmux and zsh. Used by gruvbox, catppuccin, nord and One Dark.
  The scheme file is named after the theme that introduced it; it is generic.
- **native** (`tokyonight`): the upstream plugin ships both polarities and
  equivalent integrations; `fields` name its palette keys.

Both polarities of a pair use the same engine, so `interdot toggle` never
changes the editor's semantic layout.

## Readability floor

`scripts/audit.py` computes WCAG ratios for every text/background pair the
templates draw (`uv run python scripts/audit.py [theme ...]`, `-v` for every
row; read-only, it never touches `output/`). The bar for every theme is "no worse
than the gruvbox theme of the same polarity for that same pair", capped at the
WCAG target (4.5:1 body text, 3:1 chrome). The web sheet is stricter: every
text role clears 4.5:1 on both `bg` and `bg_deep`, which is what the light
themes' `tools.web.text_darken` maps guarantee.

## Outside this repo

`interdot switch` re-themes everything this repo renders; these consumers sit
outside it and need a hand:

- **zellij** (installed on the Mac): the generated config says `theme
  "<theme-name>"` and the template ships no `themes { }` block, so every theme
  name in `config/themes/` needs `~/.config/zellij/themes/<theme-name>.kdl`
  (or a bundled zellij theme of that exact name) — `nord-light` and
  `onedarkpro-onelight` are new names. Generating that block from the palette
  is listed in TODO.md.
- **bat**: `~/.zshrc` (lines 87–96) exports `BAT_THEME` as `gruvbox-dark` /
  `gruvbox-light` from `DISPLAY_MODE`, so bat keeps gruvbox syntax colours
  under every other theme. Installed alternatives: `Nord` (nord), `OneHalfDark`
  / `OneHalfLight` (onedarkpro), nothing for catppuccin or tokyonight. A
  `tools.bat.theme` key exported from `interdot.zsh` is the proper fix (TODO.md).
- **kitty** (dormant on both machines): the config includes
  `<theme-name>.conf` relative to `~/.config/kitty/`, which holds only the
  generated `kitty.conf`; `/opt/dotfiles/kitty/` has files for
  catppuccin-frappe, catppuccin-latte, nord and tokyonight_storm only. If kitty
  comes back, copy those in and write the missing ones (gruvbox-material-*,
  nord-light, onedarkpro-*, tokyonight-day).
- **nvim** (`/opt/dotfiles/nvim`): nord and onedarkpro now render through
  `_gruvbox-material.lua`, so `lua/ui/schemes/_nord.lua`, `_onedark.lua` and
  `_catppuccin.lua` are no longer selected by any theme, gbprod/nord.nvim and
  olimorris/onedarkpro.nvim become orphaned lazy.nvim plugins (`:Lazy clean`),
  and `lua/utils.lua`'s `onedarkpro.helpers` branch plus the comment list in
  `lua/ui/colors.lua` can go. Renaming `_gruvbox-material.lua` to something
  engine-shaped (it is the generic renderer) would let `scheme:` drop the
  gruvbox name.
- **ghostty**: onedark now asks for the bundled `One Half Dark` theme instead
  of `Atom One Dark` (background `#282c34` == the editor's, where Atom's was
  `#21252b`); the new light themes use `Nord Light` and `One Half Light`.

