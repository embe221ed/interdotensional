# nord / nord-light themes

The **Nord** family on the gruvbox contract: `nord` (dark) keeps every upstream Nord hex, `nord-light` is new and pairs it, and both render Neovim through catppuccin.nvim's integration system with a Nord palette.

## Design goals

- Match Ghostty's built-in "Nord" (`#2e3440`) and "Nord Light" (`#e5e9f0`) terminal backgrounds — terminal background == editor background == leaf page
- Keep the sixteen upstream Nord hexes untouched in the dark theme (Polar Night, Snow Storm, Frost, Aurora) and only *add* the contract tokens on top of them
- Keep the theme's established identities: purple (nord15) as THE UI accent (tmux, zsh branch, nvim accent), frost ice (nord8) + aurora orange (nord12) as the leaf brand pair, nord3.5 (`#616e88`) as the quiet UI grey (`border` → catppuccin `overlay0`: NonText, fold column, the `vim.g.colors.comment` chrome roles); editor comments themselves are `overlay2` = `fg_dim`
- Keep Nord's syntax identity in the editor where catppuccin's keys allow it: keywords/operators frost blue, functions ice, strings green; types and numbers yield to the UI semantics their catppuccin keys also carry (see the mapping)
- Build the light half from doom-nord-light's darkened accents and Nord's own Polar Night / Snow Storm, swapping their roles
- Say, in the YAML, how every synthesised value was made and which floor it was made for

## Architecture

Both themes use **catppuccin.nvim as a rendering engine** with full palette overrides (`colorscheme: catppuccin`, `scheme: gruvbox-material`, flavour `mocha` / `latte`). `_gruvbox-material.lua` is the generic renderer: it reads the 26 keys from `vim.g.catppuccin_overrides`, so every catppuccin integration (Telescope, NvimTree, blink, gitsigns, noice, snacks, flash, trouble, markview, mini) is painted from the colorscheme YAML. The previous `gbprod/nord.nvim` engine had no light variant and the pair must share an engine; its function colour (nord8) survives; comments move from nord.nvim's `#616e88` to `fg_dim` (`#8b95aa`, 4.15:1), because catppuccin paints `Comment` with `overlay2`.

The two theme configs are copies of the gruvbox ones; `diff config/themes/nord.yml config/themes/nord-light.yml` touches only `name`, `polarity`, `pair`, `tmux.clock`, `ipython.pygments_style`, `ghostty.name`, `leaf.syntax`, the `text_darken` maps, `nvim.theme` and comments.

## Color palette — nord (dark)

### Accent colors

| Name | Hex | Origin | Usage |
|------|-----|--------|-------|
| red | `#bf616a` | nord11 | Errors, deletions, danger (3.05:1 on nord0 — see exceptions) |
| orange | `#d08770` | nord12 | Warm secondary: folders, selections, fzf match, leaf accent2 (4.39:1) |
| yellow | `#ebcb8b` | nord13 | Types/search/modifications, tmux prefix, zsh accents, nvim types + warnings + changed-line signs |
| green | `#a3be8c` | nord14 | Strings, success, H2 |
| aqua | `#8fbcbb` | nord7 (polar_water) | cwd, colorls links, nvim teal/sapphire (hints, docstrings, list markers) |
| blue | `#81a1c1` | nord9 (artic_water) | Info, fzf info, H3, nvim keywords + operators |
| purple | `#b48ead` | nord15 | Git badge, fzf spinner, H4/LaTeX (4.41:1) |
| pink | = purple | nord15 | THE UI accent: tmux active border/❯, zsh branch, nvim CursorLineNr/TabLineSel/lualine |
| peach | = orange | nord12 | colorls hour_old (nord's only warm that reads) |
| terracotta | = orange | nord12 | Brand warm: fzf pointer, nvim flamingo (special files) |
| maroon | `#c9939d` | synthesised: mix(nord11, nord4, 40) | Soft rose for nvim function parameters, 4.84:1 |
| ice | `#88c0d0` | nord8 | The leaf brand accent (H1, status brand, search) and nvim functions |

### Foreground scale

| Name | Hex | Origin | Contrast vs bg | Role |
|------|-----|--------|----------------|------|
| fg_primary | `#eceff4` | nord6 | 10.84:1 | fzf fg/query, interdimux query, colorls report, nvim text, leaf fg1 |
| fg_secondary | `#d8dee9` | nord4 | 9.25:1 | The standard Nord fg: leaf body (fg0), colorls normal, nvim subtext1 + lavender |
| fg_muted | `#a8b1c2` | mix(nord4, nord3.5, 40) | 5.79:1 | Inactive TOC entries, colorls file_small |
| fg_dim | `#8b95aa` | mix(nord4, nord3.5, 65) | 4.15:1 | tmux status text and pane borders, fzf header, nvim overlay2 (3.34:1 on the nord1 selection) |
| fg_faint | `#6d7992` | mix(nord4, nord3.5, 90) | 2.85:1 | Tree glyphs, zsh comments, leaf soft lines, nvim overlay1 (body text reads 3.24:1 on it) |

fg1/fg_primary is nord6 and fg0/fg_secondary is nord4 for the same reason gruvbox-material-dark puts its `fg1` in `text` and its `fg0` in the leaf body: the standard editor fg becomes the body, one step brighter becomes emphasis. Leaf therefore renders exactly as it did before (nord4 body, nord6 bold); nvim's Normal fg moves from nord4 to nord6.

### Background scale (aligned with Ghostty)

| Name | Hex | Origin | Role |
|------|-----|--------|------|
| bg_primary | `#2e3440` | nord0 | Terminal, editor and leaf page (matches Ghostty "Nord") |
| bg_deep | `#292e39` | synthesised: darken(nord0, 2.5) | Chrome: leaf TOC/status, nvim mantle (1.09:1 on nord0) |
| bg_abyss | `#232831` | synthesised: darken(nord0, 5) | nvim crust (Telescope, Noice) (1.09:1 on bg_deep) |
| panel_inset | `#3b4252` | nord1 | Selection surface: tmux menus/mode/message, interdimux current row, nvim surface0 |
| panel | `#434c5e` | nord2 | Chips: fzf selected row, leaf badges/inline code, nvim surface1 |
| panel_raised | `#4c566a` | nord3 | nvim surface2 (PmenuSel, FloatTitle) |
| border | `#616e88` | nord3 brightened (nord.nvim `polar_night.light`) | Hard lines, fzf separator — and nvim overlay0 (NonText, fold column, the `vim.g.colors.comment` UI roles: blink descriptions, Telescope directories, NvimTree indent markers, gitsigns blame, bufferline) |

Nord has nothing below nord0, so the two chrome steps are nord0 with its lightness stepped down 2.5 and 5 HLS points (hue kept).

### Grey scale

| Name | Hex | Origin | Role |
|------|-----|--------|------|
| grey0 | `#616e88` | nord3.5 (= border) | Darkest neutral |
| grey1 | `#919baf` | mix(nord4, nord3.5, 60) | leaf dim (separators, shortcuts, code labels), zsh git punctuation, nvim subtext0 — 4.47:1 (the zsh floor is 4.02) |
| grey2 | `#a8b1c2` | = fg_muted | Lightest neutral (vocabulary only) |

The greys are not one shared triple as in gruvbox: a blue-grey that reads 4.0:1 on nord0 reads 2.9:1 on nord5, so `grey1` is chosen per polarity; `grey0` (`#616e88`) and `grey2` (`#a8b1c2`) are the same hex in both themes. The whole nord4→nord3.5 line is shared: the light theme's `fg_faint` is the dark theme's `fg_dim` (`#8b95aa`) and its `grey1` is the dark theme's `fg_faint` (`#6d7992`).

## Color palette — nord-light

Sources: Ghostty "Nord Light" (background `#e5e9f0`, foreground `#414858`, selection `#d8dee9`); doom-nord-light (fg `#3b4252`, fg-alt `#2e3440`, and its darkened accents: red `#99324b`, orange `#ac4426`, green `#4f894c`, teal `#29838d`, yellow `#9a7500`, blue `#3b6ea8`, dark-blue `#5272af`, magenta `#97365b`, violet `#842879`, cyan `#398eac`, dark-cyan `#2c7088`); upstream Nord for Polar Night and Snow Storm.

### Accent colors

| Name | Hex | Origin | Contrast vs bg | Usage |
|------|-----|--------|----------------|-------|
| red | `#99324b` | doom red | 5.92:1 | as dark |
| orange | `#ac4426` | doom orange | 4.78:1 | as dark |
| yellow | `#9a7500` | doom yellow | 3.51:1 | as dark (gruvbox-light's gold sits at 3.49:1) |
| green | `#447541` | doom green `#4f894c` darkened 6 pts | 4.46:1 | as dark; raw doom green is 3.44:1, under the 4.24:1 gruvbox-light floor on seven terminal rows |
| aqua | `#24747d` | doom teal `#29838d` darkened 4 pts | 4.46:1 | as dark; raw teal is 3.65:1, under the 4.36:1 cwd/colorls floor |
| blue | `#3869a0` | doom blue `#3b6ea8` darkened 2 pts | 4.67:1 | as dark; raw blue is 4.33:1, under the 4.5:1 H3/fzf-info/colorls floor |
| purple | `#97365b` | doom magenta (nord15's seat) | 5.76:1 | as dark |
| pink | = purple | doom magenta | 5.76:1 | THE UI accent — the darkened counterpart of dark nord's pink |
| peach / terracotta | = orange | doom orange | 4.78:1 | as dark |
| maroon | `#a44d64` | synthesised: mix(red, nord5, 15) | 4.51:1 | Soft rose for nvim parameters |
| ice | `#2c7088` | doom dark-cyan | 4.56:1 | Leaf brand + nvim functions; doom's cyan `#398eac` is 3.06:1, too pale for H1/brand text |
| artic_ocean | `#5272af` | doom dark-blue | 3.93:1 | nord10's seat, unused by the config |

### Foreground scale (Polar Night; on light the "secondary" is the stronger one, as gruvbox-light)

| Name | Hex | Origin | Contrast vs bg | Role |
|------|-----|--------|----------------|------|
| fg_primary | `#3b4252` | nord1 (doom fg) | 8.26:1 | Body: fzf fg, interdimux query, colorls report, nvim text, leaf fg0 |
| fg_secondary | `#2e3440` | nord0 (doom fg-alt) | 10.26:1 | Emphasis: colorls normal, fzf label, nvim subtext1 + lavender, leaf fg1 |
| fg_muted | `#4c566a` | nord3 | 6.06:1 | Inactive TOC entries, colorls file_small |
| fg_dim | `#616e88` | nord3.5 | 4.21:1 | tmux status text/borders, fzf header, nvim overlay2 |
| fg_faint | `#8b95aa` | mix(nord3.5, nord4, 35) | 2.47:1 | Soft lines, tree glyphs, zsh comments (body text reads 3.34:1 on it; nord3.5 itself would swallow it at 1.96:1) |

### Background scale (Snow Storm stepping down; the page is the lightest)

| Name | Hex | Origin | Contrast vs bg | Role |
|------|-----|--------|----------------|------|
| bg_primary | `#e5e9f0` | nord5 | — | Page (matches Ghostty "Nord Light") |
| bg_deep | `#d8dee9` | nord4 | 1.11:1 | Chrome: leaf TOC/status, nvim mantle |
| bg_abyss | `#d0d4dd` | mix(nord5, nord3, 14) | 1.22:1 | nvim crust (1.10:1 on bg_deep) |
| panel_inset | `#d6dae3` | mix(nord5, nord3, 10) | 1.15:1 | Selection surface |
| panel | `#c6ccd5` | mix(nord5, nord3, 20) | 1.33:1 | Chips |
| panel_raised | `#bac0ca` | mix(nord5, nord3, 28) | 1.50:1 | nvim surface2 |
| border | `#aeb4c0` | mix(nord5, nord3, 36) | 1.71:1 | Hard lines, nvim overlay0 (NonText, fold column, `vim.g.colors.comment` chrome); comments are `fg_dim` = nord3.5 |

Snow Storm has only three shades, so the four raised steps and the abyss are the page mixed toward nord3 (the same hue line, greyer than doom-nord-light's bluish `base*` ladder).

### Grey scale

| Name | Hex | Origin | Role |
|------|-----|--------|------|
| grey0 | `#616e88` | nord3.5 (= fg_dim) | Darkest neutral |
| grey1 | `#6d7992` | mix(nord3.5, nord4, 10) | leaf dim, zsh punctuation, nvim subtext0 — 3.59:1 on the page, 3.24:1 on the chrome (floors 3.24 / 2.99) |
| grey2 | `#a8b1c2` | mix(nord4, nord3.5, 40) | Lightest neutral (vocabulary only) |

### text_darken

- `tools.leaf.text_darken`: `warning: 1` — the only leaf pair under its floor was the status-bar warning on the nord4 chrome (3.16:1, floor 3.23) → `#957100`, 3.35:1. Every other leaf role clears its gruvbox-light floor raw.
- `tools.web.text_darken`: `accent 3, accent2 2, success 3, info 2, warning 6, prompt_dir 1, select_fg 3` — the minimum points that put each text role at ≥4.5:1 on both `#e5e9f0` and `#d8dee9`. `special`, `danger` and `pane_active` clear it raw and carry no key.

## Catppuccin palette mapping

Both themes use the same key → token lines; only the hex differs.

```
Catppuccin key  →  Token         →  nord      nord-light   note
──────────────────────────────────────────────────────────────────────────────
rosewater       →  pink          →  #b48ead   #97365b      cursor/winbar (gruvbox line)
flamingo        →  terracotta    →  #d08770   #ac4426      special files (gruvbox line)
pink            →  pink          →  #b48ead   #97365b      builtins/markup (gruvbox line)
mauve           →  blue          →  #81a1c1   #3869a0      * keywords/conditionals = nord9, Nord's keyword colour (gruvbox: purple)
red             →  red           →  #bf616a   #99324b
maroon          →  maroon        →  #c9939d   #a44d64      parameters
peach           →  orange        →  #d08770   #ac4426      numbers/constants = nord12 (gruvbox line, see below)
yellow          →  yellow        →  #ebcb8b   #9a7500      types/classes = nord13, and warnings/git-change signs (gruvbox line, see below)
green           →  green         →  #a3be8c   #447541      strings
teal            →  aqua          →  #8fbcbb   #24747d      hints/docstrings/list markers (gruvbox line, see below)
sky             →  blue          →  #81a1c1   #3869a0      operators = nord9 (gruvbox line)
sapphire        →  aqua          →  #8fbcbb   #24747d      (gruvbox line)
blue            →  ice           →  #88c0d0   #2c7088      * functions/methods = nord8, Nord's primary accent (gruvbox: blue)
lavender        →  fg_secondary  →  #d8dee9   #2e3440      properties/namespaces = plain nord4 (gruvbox line)
text            →  fg_primary    →  #eceff4   #3b4252
subtext1        →  fg_secondary  →  #d8dee9   #2e3440
subtext0        →  grey1         →  #919baf   #6d7992
overlay2        →  fg_dim        →  #8b95aa   #616e88
overlay1        →  fg_faint      →  #6d7992   #8b95aa
overlay0        →  border        →  #616e88   #aeb4c0      NonText/fold column + vim.g.colors.comment chrome (Comment is overlay2)
surface2        →  panel_raised  →  #4c566a   #bac0ca
surface1        →  panel         →  #434c5e   #c6ccd5
surface0        →  panel_inset   →  #3b4252   #d6dae3
base            →  bg_primary    →  #2e3440   #e5e9f0
mantle          →  bg_deep       →  #292e39   #d8dee9
crust           →  bg_abyss      →  #232831   #d0d4dd
```

Two keys (`*`) deviate from the gruvbox template to keep Nord's syntax identity (`sky → blue` is the gruvbox line and happens to be Nord's operator colour). Three keys deliberately do NOT deviate, all for the same reason — a catppuccin accent key carries UI semantics as well as one syntax group, and the UI semantics win:

- `peach` stays `orange`, so numbers/constants/booleans render nord12 orange instead of Nord's nord15 purple — the `fields` block is contractually verbatim and routes `colors.orange = peach` into NvimTree folder names, Telescope matches, the outline cursor and the blame separator, all of which the terminal side paints orange (colorls dir, fzf hl, interdimux accent). Purple folders were the worse trade.
- `yellow` stays `yellow`, so types/classes/structs render nord13 yellow (light: doom yellow) instead of Nord's nord7 polar water. catppuccin's `yellow` key is also its WARNING colour — `DiagnosticWarn` (sign, virtual text, underline), `WarningMsg`, `GitSignsChange`, `NotifyWARN*`, `SnacksNotifierWarn`, the blink Class/Interface/Enum kinds, the `@comment.warning` badge — and `fields.yellow` routes it into the scheme file's `NvimTreeGitDirty` and `NotifyWARNTitle`. nord.nvim paints warnings and changed-line signs aurora yellow as well, so this keeps today's editor semantics and matches the terminal (colorls modification = yellow); nord7 types would have made every warning and every changed-line gutter sign teal.
- `teal` stays `aqua`, because the key is catppuccin's HINT colour (`DiagnosticHint`, Python docstrings via `@string.documentation`, `@markup.list` markers), not its regex/escape colour: in the installed build (`edefef7`) `@string.regexp` and `@string.escape` are the `pink` key, so no `teal` line could have restored Nord's yellow escapes anyway — they render nord15 purple.

Purple survives as the UI accent (`fields.accent = pink`) and as catppuccin's `pink`/`rosewater`. `mauve → blue` also feeds the scheme file's `colors.purple` (`purple = palette.mauve` in `colors.lua`), so the Telescope results-title background and the todo-comments `AUDIT` keyword are nord9 frost blue, not purple.

## Accepted contrast exceptions (nord, dark)

Every LOW row in the audit of `nord` comes from one of three upstream Aurora hexes that are pastel on nord0, or from the ice brand on the nord2 chip. Changing them would stop the theme being Nord (every Nord port — nord.nvim, doom-nord, the Ghostty/kitty/iTerm schemes — renders these exact values), so they are kept and marked inline in `config/themes/nord.yml`. None is body text; `nord-light` has no exceptions (130/130).

| Hex | Rows | Ratio (floor) |
|-----|------|---------------|
| red `#bf616a` (nord11) | leaf alert caution, interdimux danger, zsh red, colorls dead_link/error/deletion, web danger on bg | 3.05:1 (4.5) |
| red on the tinted error badge / on bg_deep | leaf status error; web danger on bg_deep | 2.82:1 (4.26) / 3.32:1 (4.5) |
| orange `#d08770` (nord12) on nord0 | leaf H5+/mermaid kw, web accent2, interdimux accent + menu_sel_fg, fzf hl + prompt, colorls dir/file_large/untracked/hour_old | 4.39:1 (4.5) |
| orange on the nord1 selection | tmux menu/mode/message, web select_fg, interdimux match_current | 3.54:1 (4.5) |
| orange on the nord2 chip | leaf inline code, fzf hl on selected row | 3.03:1 (4.5) |
| purple `#b48ead` (nord15) on nord0 | leaf H4, web special + pane_active, tmux active window, interdimux git, zsh magenta, fzf spinner, colorls read/exec/day_old | 4.41:1 (4.5) |
| purple on/under nord1 and nord2 | tmux copy-mode current match (nord1 on purple); leaf inline LaTeX on nord2 | 3.55:1 (4.5); 3.05:1 (4.23) |
| ice `#88c0d0` (nord8) on nord2 | leaf status search chip | 4.31:1 (4.5) |

Everything else — frost blue/teal, yellow, green, the whole text ladder, every line and surface — is at or above the gruvbox-material-dark ratio for the same pair.

## Other per-theme choices

- `tmux.clock`: dark `173` (`#d7875f`, nearest to nord12 orange, 4.47:1 on nord0 — the contract's "warm accent visible on bg"; nord15 purple's 139 is not warm and reads 4.11:1); light `130` (`#af5f00`, nearest to the orange).
- `ipython.pygments_style`: dark `nord`; light `lovelace` — no light Nord style is installed and lovelace is the cool, desaturated light one (the other light styles are warm or high-saturation).
- `ghostty.name`: `Nord` / `Nord Light`; `kitty`: both blocks empty, so the template emits `include nord.conf` / `include nord-light.conf`, resolved relative to `~/.config/kitty/`. kitty is dormant on both machines; `/opt/dotfiles/kitty/nord.conf` exists, `nord-light.conf` does not (see docs/theme-contract.md, "Outside this repo").
- `leaf.syntax`: `base16-ocean.dark` / `base16-ocean.light`.

## Files

### Interdotensional
- `colorschemes/nord.yml`, `colorschemes/nord-light.yml` — palettes (single source of truth, one hex per colour via YAML anchors)
- `config/themes/nord.yml`, `config/themes/nord-light.yml` — tool configs with `$token$` refs

### Neovim
- `lua/ui/schemes/_gruvbox-material.lua` — the catppuccin renderer both themes use (overrides from `vim.g.catppuccin_overrides`); `_nord.lua` (gbprod/nord.nvim) is no longer selected by this family

### Generated
- `output/nvim/globals.lua` — includes `vim.g.catppuccin_overrides` table
- `output/nvim/colors.lua` — semantic color mapper
- `output/colorls/dark_colors.yaml` / `light_colors.yaml` — file listing colors (hex values; the light template renders for nord-light)
- `output/tmux/.tmux.conf` — status/pane/copy-mode colours
- `output/zsh/theme.zsh-theme` — prompt colours (truecolor hex)
- `output/leaf/theme.toml` — leaf markdown reader theme (role-driven via `tools.leaf`)
- `output/web/interdot-theme.css` — both polarities, switched in the browser
