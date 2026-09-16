# onedarkpro theme family (onedark / onelight)

The user's **One Dark** theme (`onedarkpro-onedark`, the existing dark theme) and its new light pair **One Light** (`onedarkpro-onelight`, named after onedarkpro.nvim's own `onelight` variant), both implemented to the gruvbox contract: the 28 contract tokens laid over the upstream palette with YAML anchors, the gruvbox theme config copied line for line with only the per-theme deviations the contract allows, and Neovim rendered through the same catppuccin-with-overrides engine gruvbox uses.

## Design goals

- Terminal background == editor background == the ghostty theme's `background`: `#282c34` (One Half Dark) and `#fafafa` (One Half Light). The dark theme moves from ghostty's `Atom One Dark` (background `#21252b`, which never matched the editor's `#282c34`) to `One Half Dark`, whose palette is the exact One Dark set.
- Keep every existing One Dark hex: the 16 tokens the dark colorscheme already had are byte-identical; the contract tokens anchor to them, and the few steps One Dark does not have are synthesised with the pipeline's own `darken()` / `mix()` filters, so every derived value is reproducible.
- Keep the established UI identity: `pink` (the accent everywhere — tmux active border and `❯`, fzf border, zsh branch, nvim `fields.accent`) is One Dark's purple, as `tools.tmux.colors.pink` already was; the leaf reader stays orange brand + purple secondary; fzf's pointer stays red.
- The light pair is derived from onedarkpro's `onelight` palette and the One Half Light terminal theme, darkened only as far as the gruvbox-light floors need.
- Readability floors pair by pair from the gruvbox theme of the same polarity. The light theme clears every one. The dark theme keeps two upstream One Dark values that fall short (red, purple-on-a-chip) plus a faint grey squeezed between two floors; each is named in the YAML and in the last section.

## Architecture

Both themes now use `colorscheme: "catppuccin"`, `scheme: "gruvbox-material"` — `_gruvbox-material.lua` reads `vim.g.catppuccin_overrides` (generated), replaces catppuccin.nvim's `mocha` / `latte` palette with the 26 overrides and applies the user's custom highlights and integrations. The previous dark setup (`olimorris/onedarkpro.nvim`, `vanilla: true`, `_onedark.lua`) applied no custom highlights at all, and onedarkpro's `onelight` would have been a second engine for the pair; the contract's family decision is one engine for both polarities. The `plugin:` spec is now the one-line catppuccin spec; onedarkpro.nvim is no longer loaded by this theme.

Outside nvim the contract tokens feed tmux, fzf, interdimux (new to this family — the 15 gruvbox keys verbatim), zsh (moved from 256-colour indexes `204/38/39/114/180/170` to the palette hex roles), colorls (the 29-key gruvbox mapping), leaf and the web stylesheet (`tools.web.prompt_dir: $aqua$`, plus the light theme's `text_darken` map).

## Contract tokens — onedark (dark)

Ratios are on `bg #282c34` unless stated. "Origin" names the upstream token or the formula.

### Accents

| Token | Value | Origin | Contrast | Role |
|-------|-------|--------|----------|------|
| red | `#e06c75` | onedark red | 4.38:1 | errors / danger (interdimux, leaf, zsh ✘, colorls, nvim red). 0.1 short of AA — kept, see exceptions |
| orange | `#d19a66` | onedark orange | 5.68:1 | warm secondary: tmux selection text, fzf hl/prompt, interdimux accent, leaf brand, colorls dirs, nvim peach (numbers) |
| yellow | `#e5c07b` | onedark yellow | 8.10:1 | tmux prefix ●/zoom, fzf marker, interdimux path, leaf warning, zsh accents, nvim yellow (types) |
| green | `#98c379` | onedark green | 6.94:1 | success: leaf H2/tips, zsh ❯, colorls exec files, nvim green (strings) |
| aqua | `#56b6c2` | = cyan | 5.91:1 | zsh cwd, web prompt_dir, colorls links, nvim teal/sapphire |
| blue | `#61afef` | onedark blue | 5.92:1 | info: fzf info, interdimux ssh, leaf H3/links, nvim blue/sky (functions, operators) |
| purple | `#c678dd` | onedark purple | 4.75:1 | fzf spinner, interdimux git badge, leaf H4/LaTeX + accent2, nvim mauve (keywords) |
| pink | `#c678dd` | = purple | 4.75:1 | THE UI accent: today's `tools.tmux.colors.pink`, kept |
| peach | `#d8836e` | **synthesised**: `mix(orange, red, 50)` | 4.93:1 | colorls hour_old — the mid warm between One Dark's two warms (the contract's "second warm between orange and red") |
| terracotta | `#e06c75` | = red | 4.38:1 | fzf pointer (today's identity: the pointer was already `$red$`), nvim flamingo. Orange would collide with hl/prompt |
| maroon | `#e06c75` | = red | 4.38:1 | nvim parameters (`@variable.parameter`): One Dark paints them red, so the token aliases red instead of the contract's soft-rose guidance (see the mapping section). nvim is its only consumer |

### Text ladder

One Dark ships exactly one neutral text colour (`fg` and `white` are both `#abb2bf`), so three steps are synthesised (two below fg, and the faint grey two darken points below One Dark's gray) and the emphasis step comes from the One Half Dark terminal theme.

| Token | Value | Origin | Contrast | Role |
|-------|-------|--------|----------|------|
| fg_primary | `#abb2bf` | onedark fg | 6.57:1 | fzf fg/query, interdimux query, colorls report, nvim text |
| fg_secondary | `#9fa7b6` | **synthesised**: `darken(fg, 4)` | 5.78:1 | fzf label, colorls normal, nvim subtext1/lavender — the slightly quieter step below fg |
| fg_muted | `#959ba6` | **synthesised**: `mix(fg, comment, 50)` | 5.01:1 (5.51:1 on bg_deep) | leaf inactive TOC entries, colorls file_small. onedarkpro's comment grey itself is 4.10:1 on bg_deep, under the 4.5 floor |
| fg_dim | `#7f848e` | onedark comment | 3.73:1 (3.47:1 on the cursorline) | tmux status text and inactive borders (today's `dim`), fzf/interdimux headers, colorls no_access, nvim overlay2 |
| fg_faint | `#575e6a` | **synthesised**: `darken(gray, 2)` | 2.14:1 (body text reads 3.06:1 on it) | zsh comments, interdimux/colorls tree lines, leaf soft lines and search-highlight surface, nvim overlay1 (Conceal, unchecked list items). Two points below One Dark's gray `#5c6370` (2.32:1, kept as `grey0`), the darkest grey that keeps leaf body text on the search highlight at 3.0:1. See exceptions |
| fg0 | `#abb2bf` | = fg_primary | 6.57:1 | leaf body — the same text nvim and the terminal use (today's leaf body) |
| fg1 | `#dcdfe4` | One Half Dark foreground (ghostty palette 7/15) | 10.48:1 | leaf emphasis (bold, active TOC, marks). The brighter step the brief asks for; a real family value (the terminal's own default text once ghostty is on One Half Dark) and the only step that keeps `<mark>` text above gruvbox's 4.0 (5.03:1 on the orange mark; `#abb2bf` reads 3.15) |

### Surfaces (dark ordering: bg_abyss < bg_deep < bg_primary < panel_inset < panel < panel_raised < border)

| Token | Value | Origin | On bg | Role |
|-------|-------|--------|-------|------|
| bg_primary | `#282c34` | onedark bg | 1.00 | terminal/editor background (= ghostty "One Half Dark") |
| bg_deep | `#21252b` | Atom One Dark's sidebar/tab-bar grey (= ghostty "Atom One Dark" background) | 1.10 | leaf TOC/status bar, nvim mantle (NvimTree, Noice) |
| bg_abyss | `#1a1e22` | **synthesised**: `darken(bg_deep, 3)` | 1.20 (1.09 on bg_deep) | nvim crust (Telescope, NoicePopup) |
| panel_inset | `#2d313b` | onedark cursorline | 1.08 | tmux menu/mode/message bg, interdimux current row, nvim surface0 (today's tmux selection surface) |
| panel | `#353b45` | **synthesised**: the step between cursorline and selection | 1.24 (1.15 on the cursorline) | fzf selected row, leaf chips (badges, inline code, active TOC row), nvim surface1. Orange reads 4.58:1 on it |
| panel_raised | `#414858` | onedark selection | 1.53 | nvim surface2 (PmenuSel, FloatTitle, bufferline separators) |
| border | `#4b5263` | Atom One Dark's gutter (line-number) grey | 1.79 | fzf separator/scrollbar, interdimux separator/border, leaf rules/heading underline/table separators, nvim overlay0 (NonText, the fold column, inactive tabline text, Pmenu extra text) and, through `fields.comment`, the `vim.g.colors.comment` UI roles |

nvim comments do not change with the engine switch: catppuccin paints `Comment` / `@comment` with `overlay2` = `fg_dim` = `#7f848e` (3.73:1), which is onedarkpro.nvim's own `comment` grey. `border` (overlay0) never carries comment text; `fields.comment = overlay0` only feeds `vim.g.colors.comment`, whose consumers are the blink label description, the Telescope directory, NvimTree indent markers, the gitsigns current-line blame, bufferline close/visible buffers and the lualine section-b background.

### Greys (shared by both polarities, like gruvbox's triple)

| Token | Value | Origin | Dark / light contrast | Role |
|-------|-------|--------|-----------------------|------|
| grey0 | `#5c6370` | onedark gray | 2.32 / 5.79 | darkest neutral (vocabulary) |
| grey1 | `#868b94` | **synthesised**: `mix(onedark comment, onelight comment, 25)` | 4.09 / 3.28 | leaf chrome text, zsh git punctuation/venv/jobs, nvim subtext0. The one value that clears zsh's floor in both polarities (4.02 dark, 3.24 light) |
| grey2 | `#9b9fa6` | onelight comment | 5.27 / 2.55 | lightest neutral (the light theme's `fg_faint`) |

## Contract tokens — onelight (light)

Identity source: onedarkpro.nvim's `onelight` palette (`bg #fafafa`, `fg #6a6a6a`, `gray #bebebe`, `comment #9b9fa6`, `highlight #e2be7d`) and the One Half Light terminal theme (ghostty `One Half Light`: background `#fafafa`, foreground `#383a42`, red `#e45649`, green `#50a14f`, yellow `#c18401`, blue `#0184bc`, magenta `#a626a4`, cyan `#0997b3`). Ratios are on `bg #fafafa` unless stated.

### Accents

Every onelight and One Half Light accent except One Half Light's magenta is too pale for its floor on `#fafafa` (onelight: red 3.55, orange 2.33, yellow 1.96, green 2.99, cyan 2.27, blue 3.58, purple 3.40; One Half Light: red 3.51, yellow 3.06, green 3.07, cyan 3.30, blue 4.00). Following the brief — prefer the One Half Light value of the hue — each contract accent is the One Half Light hue (onelight's for orange, which One Half Light lacks) stepped down with the repo's `darken()` to the first integer step that clears every consumer's floor.

| Token | Value | Origin | Contrast | Floor it had to clear |
|-------|-------|--------|----------|-----------------------|
| red | `#da3020` | `darken(One Half Light red #e45649, 10)` | 4.55:1 | 4.5 — fzf pointer (via terracotta); also above zsh/interdimux/colorls' 4.26 |
| orange | `#bd6b0f` | `darken(onelight orange #ee9025, 14)` | 3.82:1 | 3.76 — fzf hl/prompt, interdimux accent, colorls dir; 3.28 on the selection surface (tmux menus, floor 3.24) |
| yellow | `#b27a01` | `darken(One Half Light yellow #c18401, 3)` | 3.54:1 | 3.49 — tmux prefix flag, zsh accents, fzf marker, colorls; selection text on it 3.05 (copy-mode match, floor 3.01) |
| green | `#428642` | `darken(One Half Light green #50a14f, 8)` | 4.26:1 | 4.24 — zsh ❯, interdimux editor/success, colorls, leaf H2 |
| aqua | `#087e96` | `darken(One Half Light cyan #0997b3, 6)` | 4.54:1 | 4.36 — zsh cwd, colorls links (the web prompt_dir darkens it 1 point to `#087a91`: 4.79 on bg, 4.54 on bg_deep) |
| blue | `#0179ad` | `darken(One Half Light blue #0184bc, 3)` | 4.64:1 | 4.5 — fzf info, interdimux ssh, leaf H3, colorls |
| purple | `#a626a4` | One Half Light magenta, as it is | 5.86:1 | 4.44 — clears everything raw, including inline code on the chip (4.68) |
| pink | `#a626a4` | = purple | 5.86:1 | THE UI accent: the light counterpart of onedark's purple |
| peach | `#c34b17` | `darken(mix(orange, red, 50), 2)` | 4.64:1 | 4.5 — colorls hour_old (the raw mix is 4.31) |
| terracotta | `#da3020` | = red | 4.55:1 | 4.5 — fzf pointer, nvim flamingo (as in the dark pair) |
| maroon | `#da3020` | = red | 4.55:1 | nvim parameters — red, as in the dark pair |

### Text ladder (light: fg_secondary is the darker, emphasis step, as in gruvbox-light)

| Token | Value | Origin | Contrast | Role |
|-------|-------|--------|----------|------|
| fg_primary | `#383a42` | One Half Light foreground (= Atom One Light's editor fg) | 10.86:1 | main text. onelight's own `fg #6a6a6a` (5.18) is too light to lead a ladder |
| fg_secondary | `#2c2e34` | **synthesised**: `darken(fg_primary, 5)` | 13.0:1 | fzf label, colorls normal, nvim subtext1/lavender, and `fg1`. One Light has no neutral below its fg |
| fg_muted | `#6a6a6a` | onelight fg | 5.18:1 (4.92:1 on bg_deep) | leaf inactive TOC entries, colorls file_small |
| fg_dim | `#7f848e` | onedark comment | 3.60:1 (3.09:1 on the selection) | tmux status text, fzf/interdimux headers, colorls no_access — the same hex in both polarities, as gruvbox's fg_dim is |
| fg_faint | `#9b9fa6` | onelight comment | 2.55:1 | zsh comments, tree lines, leaf soft lines (body text reads 4.27:1 on the search highlight). onelight's `gray #bebebe` is 1.78, under the 2.21 floor |
| fg0 | `#383a42` | = fg_primary | 10.86:1 | leaf body |
| fg1 | `#2c2e34` | = fg_secondary | 13.0:1 | leaf emphasis |

### Surfaces (light: bg_primary is the lightest; chrome and raised sides step down)

All six are `darken(bg, N)` with onedarkpro's own generated-shade amounts for onelight (`cursorline` 2.5, `float_bg` 4.5, `selection` 6.5, `fg_gutter` 9.7, `line_number` 18); only the 13 is an interpolated step.

| Token | Value | Origin | On bg | Role |
|-------|-------|--------|-------|------|
| bg_primary | `#fafafa` | onelight bg | 1.00 | page/terminal background (= ghostty "One Half Light") |
| bg_deep | `#f4f4f4` | `darken(bg, 2.5)` — cursorline / statusline | 1.05 | leaf chrome, nvim mantle, the web's code-block ground. Exactly the contract minimum; the next onedarkpro shade (`#efefef`, 1.10) would drop leaf dim-on-chrome to 2.98 (floor 2.99) and the status warning to 3.22 (floor 3.23) and cost every web role one more darken point |
| bg_abyss | `#efefef` | `darken(bg, 4.5)` — float_bg | 1.10 | nvim crust. 1.045 on bg_deep, within the contract's "~1.05"; kept as onedarkpro's own shade since crust is its only consumer |
| panel_inset | `#e9e9e9` | `darken(bg, 6.5)` — selection | 1.16 | tmux selection/menus, interdimux current row, nvim surface0 |
| panel | `#e1e1e1` | `darken(bg, 9.7)` — fg_gutter | 1.25 | fzf selected row, leaf chips, nvim surface1 |
| panel_raised | `#d9d9d9` | `darken(bg, 13)` — interpolated | 1.35 | nvim surface2 |
| border | `#cccccc` | `darken(bg, 18)` — line_number | 1.54 | hard lines; nvim overlay0 (NonText, fold column, `vim.g.colors.comment` UI roles — not comments, see the dark table). gruvbox-light's border is 1.51 |

### Greys

The same triple as onedark: `grey0 #5c6370`, `grey1 #868b94` (3.28:1 — zsh git punctuation, floor 3.24), `grey2 #9b9fa6` (= fg_faint).

## Catppuccin palette mapping (nvim)

The gruvbox template for every override key, with one token-level deviation. One Dark's keywords (purple), functions (blue), numbers/constants (orange), types (yellow) and strings (green) are what catppuccin paints with `mauve`, `blue`, `peach`, `yellow` and `green`, so those keys follow the template. One Dark's other signature — identifiers in red (`@variable`, `@variable.parameter`, `@variable.member` and `@property` are all `red` in onedarkpro.nvim, `Identifier` too) — only partly survives the engine, and the doc is honest about which parts:

- `maroon` aliases `red` in both colorschemes (`#e06c75` / `#da3020`) instead of the contract's soft rose, so function parameters (`@variable.parameter`) read One Dark red as upstream. `maroon`'s only consumer is nvim (that group, blink's TypeParameter kind, a few dap/neotest groups), so the audit gains no rows; `peach` stays the synthesised mid warm for colorls `hour_old`.
- `lavender` keeps the template line (`fg_secondary`), so fields and properties (`@variable.member`, `@property`) render as the near-fg grey `#9fa7b6` / `#2c2e34`, not red. Mapping `lavender → red` would also paint the danger colour onto chrome that catppuccin routes through that key alone: `NvimTreeRootFolder`, `NoiceCmdlinePopupBorder`, `FlashMatch`, `RenderMarkdownTableRow`, `SnacksDashboardFile`, `UfoFoldedFg`, `MasonHeading`, `Tag`, markdown H6 and `@markup.link` labels. The UI semantics win, as in nord.
- `@variable` is catppuccin's `text` key (= fg), and no override can recolour it without recolouring all body text, so plain variables are `#abb2bf` / `#383a42`, not red.

```
Catppuccin key  →  Colorscheme token  →  onedark    onelight
──────────────────────────────────────────────────────────────
rosewater       →  pink               →  #c678dd    #a626a4
flamingo        →  terracotta         →  #e06c75    #da3020
pink            →  pink               →  #c678dd    #a626a4
mauve           →  purple             →  #c678dd    #a626a4
red             →  red                →  #e06c75    #da3020
maroon          →  maroon             →  #e06c75    #da3020   (= red, see below)
peach           →  orange             →  #d19a66    #bd6b0f
yellow          →  yellow             →  #e5c07b    #b27a01
green           →  green              →  #98c379    #428642
teal            →  aqua               →  #56b6c2    #087e96
sky             →  blue               →  #61afef    #0179ad
sapphire        →  aqua               →  #56b6c2    #087e96
blue            →  blue               →  #61afef    #0179ad
lavender        →  fg_secondary       →  #9fa7b6    #2c2e34
text            →  fg_primary         →  #abb2bf    #383a42
subtext1        →  fg_secondary       →  #9fa7b6    #2c2e34
subtext0        →  grey1              →  #868b94    #868b94
overlay2        →  fg_dim             →  #7f848e    #7f848e
overlay1        →  fg_faint           →  #575e6a    #9b9fa6
overlay0        →  border             →  #4b5263    #cccccc
surface2        →  panel_raised       →  #414858    #d9d9d9
surface1        →  panel              →  #353b45    #e1e1e1
surface0        →  panel_inset        →  #2d313b    #e9e9e9
base            →  bg_primary         →  #282c34    #fafafa
mantle          →  bg_deep            →  #21252b    #f4f4f4
crust           →  bg_abyss           →  #1a1e22    #efefef
```

Consequences worth knowing versus the old onedarkpro.nvim rendering: comments are unchanged (`overlay2` = `#7f848e`, see above); `fields` are the gruvbox lines verbatim, so `vim.g.colors` maps `orange → peach` (folders, Telescope matches), `accent → pink` (= purple: CursorLineNr, TabLineSel, lualine/bufferline selection), `alt_fg → surface2` (= selection), `comment → overlay0` (= border `#4b5263`: blink descriptions, Telescope directories, NvimTree indent markers, gitsigns blame, bufferline close buttons, the lualine section-b background).

## Light-theme derivation (onelight)

What is pinned and what is derived:

- **Pinned raw**: `bg #fafafa` (onelight bg = One Half Light background), `fg_primary #383a42` (One Half Light foreground), `fg_muted #6a6a6a` (onelight fg), `fg_faint #9b9fa6` (onelight comment), `purple`/`pink #a626a4` (One Half Light magenta), `fg_dim #7f848e` and the grey triple (shared with the dark theme).
- **Derived with `darken()`**: the six accents in the table above, `peach = darken(mix(orange, red, 50), 2)`, `fg_secondary = darken(fg_primary, 5)`, and every surface as `darken(bg, N)` with onedarkpro's own shade amounts.
- **Not used**: onelight's `red #e05661`, `yellow #eea825`, `green #1da912`, `cyan #56b6c2`, `blue #118dc3`, `purple #9a77cf` (all under their floors, and One Half Light's hue is what the terminal palette shows) and `gray #bebebe` (1.78:1). onelight's `orange #ee9025` is the derivation source for `orange`, since One Half Light has no orange slot.

The two `text_darken` maps then carry the accents where they are text:

| Map | Key | Points | Result | Why |
|-----|-----|--------|--------|-----|
| leaf | accent | 4 | orange → `#aa600d` | 4.58:1 as H1 (floor 4.23), 3.66 on the chip as the search badge (floor 3.3), 4.35 on the chrome as the percent (floor 3.91). 3 points (`#af630e`, 4.36 as H1, 3.48 on the chip, 4.14 on the chrome) already clears every leaf floor; 4 is kept so H1 reaches WCAG's 4.5 on bg and to match gruvbox-light's `accent: 4` |
| leaf | accent2 | 0 | purple as it is | 4.68 on the chip, 5.56 on the chrome |
| leaf | warning, success | — (absent) | yellow 3.54 / 3.36 on bg / bg_deep (floors 3.49 / 3.23); green 4.26 as H2 and 3.40 on the watch badge (floors 4.24 / 3.31) | raw values already clear their floors |
| web | accent / success / info / warning / danger | 5 / 3 / 1 / 6 / 2 | `#a55e0d` / `#3d7c3d` / `#0175a8` / `#946501` / `#d12e1f` | the minimum points that clear 4.5:1 on BOTH bg `#fafafa` and bg_deep `#f4f4f4` (the second is always the binding one) |
| web | accent2 / special / pane_active | 0 | purple `#a626a4` | 5.86 / 5.56 raw |
| web | prompt_dir | 1 | aqua → `#087a91` | 4.79 on bg, 4.54 on bg_deep (raw aqua is 4.54 / 4.31, under the 4.5 on bg_deep the map must guarantee) |
| web | select_fg | 7 | orange → `#9c580c` | 4.53 on the `#e9e9e9` selection surface |

The dark theme has no map: a dark theme never darkens, and every dark role but `danger` clears AA on both grounds (red: 4.38 on bg, 4.82 on bg_deep).

## Other per-theme choices

| Key | onedark | onelight |
|-----|---------|----------|
| `tmux.clock` | 173 (`#d7875f`), nearest xterm-256 index to orange `#d19a66`, the warm accent (was 170 `#d75fd7`, a magenta near the purple) | 130 (`#af5f00`), nearest to orange `#bd6b0f` |
| `ipython.pygments_style` | `one-dark` — the family's own installed style, unchanged | `paraiso-light` — the closest installed light style in hue: purple keywords, green strings, orange numbers, cyan-blue functions on a light ground, i.e. One Light's own assignment. `xcode` has the same magenta keywords but red strings; `friendly`/`default` are blue/green-led |
| `ghostty.name` | **`One Half Dark`** (background `#282c34` = bg; foreground `#dcdfe4` = fg1; ANSI 1–6 are the One Dark accents). Was `Atom One Dark`, whose background `#21252b` never matched the editor — that grey is now `bg_deep`. Reversible: it is one line in `config/themes/onedarkpro-onedark.yml`; nothing else keys off the name | `One Half Light` (background `#fafafa` = bg, foreground `#383a42` = fg_primary) |
| `kitty` | empty — kitty is dormant and `/opt/dotfiles/kitty/` has no One Dark file, so the template includes `onedarkpro-onedark.conf` | empty — includes `onedarkpro-onelight.conf` |
| `leaf.syntax` | `base16-ocean.dark` | `base16-ocean.light` |
| `leaf.accent` / `accent2` | orange / purple (the existing leaf identity) | orange / purple (their light counterparts) |
| `nvim.theme` | `mocha` | `latte` |

## Accepted contrast exceptions

Floor = min(WCAG target, the same pair in the gruvbox theme of the same polarity). **onelight has none** (130/130 pairs at or above the floor). onedark keeps 14 rows below the floor: 12 caused by two upstream One Dark hexes (red, purple) that are kept because they are the palette's identity, and 3 by the synthesised faint grey; every affected line in `config/themes/onedarkpro-onedark.yml` carries the ratio inline. None is body text.

| Cause | Ratio | Floor | Rows |
|-------|-------|-------|------|
| `red #e06c75` on bg `#282c34` — One Dark's red is 0.1 short of AA; no One Dark-family red clears 4.5 (One Half Light's `#e45649` is 3.82 on this bg, onedarkpro's vivid `#ef596f` 4.22) | 4.38 | 4.5 | leaf alert caution; web danger on bg; interdimux danger; zsh red; colorls dead_link, error, deletion (7) |
| `red` on leaf's tinted error badge `#3e3036` (mix(red, bg_deep, 85)) | 3.91 | 4.26 | leaf status error (1) |
| `purple #c678dd` on the chip `#353b45` — purple is 4.75 on bg itself, and the only surface it reads 4.5 on is bg; even the cursorline (the lowest legal chip) gives 4.42. Purple is `accent2` (the leaf identity) and `special` (the contract) | 3.83 | 4.5 (inline code) / 4.23 (inline LaTeX) | leaf inline code; leaf LaTeX inline (2) |
| cursorline `#2d313b` as text on `pink` (purple) — tmux copy-mode current match; the selection surface cannot go darker than the cursorline and stay visible on bg | 4.42 | 4.5 | tmux copy current match (1) |
| `fg_faint #575e6a` (`darken(gray, 2)`) on bg — the comment/tree grey. `fg_faint` is squeezed between two floors that One Dark's `fg` (6.57:1) cannot satisfy at once: a grey bright enough for zsh comments at gruvbox's 2.59 puts leaf body text on the search highlight at 2.54, and the contract forbids exceptions for body text. So the grey is the brightest step that keeps body text at 3.0:1 there (3.06; One Dark's gray itself, 2.32:1 on bg, gave 2.84) and the comment side takes the hit | 2.14 | 2.59 | zsh comment; colorls no_modifier, tree (3) |

One ordering waiver, not a contrast exception: `panel_inset` is One Dark's cursorline `#2d313b`, 1.08:1 on bg, where the contract prose asks for 1.1:1. The audit tolerance passes it, the brief pins the cursorline for this slot, and it is today's tmux menu/mode surface; a synthesised chip for the sake of 0.02 would change the live tmux selection for no readable gain.

## Files

### Interdotensional
- `colorschemes/onedarkpro-onedark.yml`, `colorschemes/onedarkpro-onelight.yml` — palettes (single source of truth; upstream names kept, contract tokens as anchors)
- `config/themes/onedarkpro-onedark.yml`, `config/themes/onedarkpro-onelight.yml` — tool configs with `$token$` refs; they `pair:` each other and diff only on the contract's per-polarity list

### Neovim
- `lua/ui/schemes/_gruvbox-material.lua` — catppuccin setup with colour overrides from `vim.g.catppuccin_overrides` (shared with gruvbox, catppuccin and nord); `_onedark.lua` is no longer selected by this family

### Generated
- `output/nvim/globals.lua` — `vim.g.colorscheme` (catppuccin / gruvbox-material / mocha or latte) + `vim.g.catppuccin_overrides`
- `output/nvim/colors.lua` — semantic colour mapper (gruvbox `fields`)
- `output/colorls/dark_colors.yaml` / `light_colors.yaml` — file listing colours (hex; onelight renders the light file)
- `output/tmux/.tmux.conf` — theme, status, copy-mode and interdimux colours
- `output/zsh/theme.zsh-theme`, `output/zsh/interdot.zsh` — prompt colours (hex roles) and the comment highlight
- `output/fzf/fzf-colors.sh` — fzf palette
- `output/leaf/theme.toml` — leaf markdown reader theme (role-driven via `tools.leaf`)
- `output/web/interdot-theme.css` — both polarities, switched in the browser
- `output/ghostty/config`, `output/kitty/kitty.conf`, `output/ipython/ipython_config.py` — `theme = One Half Dark|Light`, `include onedarkpro-<variant>.conf`, `theme.base = "one-dark"|"paraiso-light"`
