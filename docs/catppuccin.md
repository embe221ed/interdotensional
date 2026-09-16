# catppuccin theme family (frappe / latte)

The two catppuccin flavours the user runs — **frappe** (dark) and **latte** (light) — implemented to the gruvbox contract: every upstream catppuccin hex kept verbatim under a `ctp:` map that only the nvim overrides read, the 28 contract tokens laid over it as YAML aliases on frappe and — where latte's pastels cannot carry terminal text — as ink variants derived with the pipeline's own `darken()` (plus a handful of synthesised steps where catppuccin's compressed ramps have no step to offer), and Neovim rendered through the same catppuccin-with-overrides engine gruvbox uses.

## Design goals

- Terminal background == editor background == the ghostty theme's `background`: `#303446` (frappe `base`) and `#eff1f5` (latte `base`)
- Keep every upstream catppuccin hex exactly; the user's two hand tweaks — frappe `lavender #b4b5ee` (upstream `#babbf1`) and latte `peach #f28d5e` (upstream `#fe640b`) — are the `ctp:` values, and the `*_bak` cruft is gone
- Neovim is **identity**: the 26 `catppuccin_overrides` name their own upstream colour, so the editor is exactly catppuccin (plus the two tweaks) and the yml is the single source of truth — the tweaks no longer live in Lua
- Keep the established UI identity: `pink` is the accent everywhere (tmux, fzf border, zsh branch, nvim `fields.accent`; on latte the terminal's pink is the ink variant and the editor's the pastel), the leaf reader stays pink brand + teal secondary
- Readability floors pair-by-pair from the gruvbox theme of the same polarity: latte clears all 130 audited pairs because its terminal-facing accents are ink variants of the latte hues; frappe keeps two leaf exceptions (last section, which also says how to put latte's terminal back on the raw pastels)

## Architecture

Both themes now use `scheme: "gruvbox-material"` — `_gruvbox-material.lua` reads `vim.g.catppuccin_overrides` (generated), replaces catppuccin.nvim's `frappe` / `latte` palette with it and applies the user's custom highlights and integrations. Because every override points at its own upstream name in the colorscheme's `ctp:` map (`rosewater: "$ctp.rosewater$"` … `crust: "$ctp.crust$"`), the **palette** is byte-for-byte upstream catppuccin except `lavender` (frappe) and `peach` (latte). The **highlight layer** is now the shared gruvbox-material engine rather than the retired `_catppuccin.lua` (which hard-coded those two tweaks in Lua), and a few catppuccin-specific tweaks of that file go with it: `NvimTreeSpecialFile` is peach (`colors.orange`) instead of flamingo, `@parameter.readonly` / `@parameter.modification` are no longer maroon italic, `NotifyTRACETitle` is pink instead of rosewater, `TelescopeTitle` (cyan) and `TelescopePromptCounter` are dropped, `styles.miscs = {}` turns off catppuccin's hard-coded italics on misc groups, and `GitSignsCurrentLineBlame` / `…Sep` styling is added. The integrations block is the same. Latte's `winblend` goes from 15 to the contract's 0 and `alt_fg` from `surface1` to `surface2`, like gruvbox.

The contract tokens exist for everything *outside* nvim: tmux, fzf, interdimux, zsh, colorls, leaf and the web stylesheet. Two facts shape the choices below:

1. The keys `red yellow green blue pink maroon peach` are **both** upstream names and contract tokens, so the upstream palette lives under a `ctp:` map (`$ctp.pink$` …) that only the nvim overrides read. On frappe every contract token aliases its `ctp:` value. On latte the shared names whose pastels cannot carry terminal text (`pink yellow green blue`), `peach` (= terracotta) and the contract-only accents `orange aqua terracotta` carry ink variants derived with `darken()`; `red` and `maroon` alias (`red` clears its floors, `maroon` has no terminal consumer).
2. Catppuccin's neutral ramp (`crust … text`) is compressed compared with gruvbox's, so two steps the contract needs do not exist and are synthesised from their neighbours (frappe `panel_inset`, frappe `fg_faint`, latte `fg_secondary`).

## Contract tokens — frappe (dark)

### Accents

| Token | Value | Origin | Contrast on bg | Role |
|-------|-------|--------|----------------|------|
| red | `#e78284` | red | 4.65:1 | errors / danger (interdimux, leaf, zsh ✘, colorls, nvim red) |
| orange | `#ef9f76` | = peach | 5.80:1 | warm secondary: tmux selection text, fzf hl/prompt, interdimux accent, colorls dirs (catppuccin has no orange) |
| yellow | `#e5c890` | yellow | 7.62:1 | tmux prefix ●/zoom, fzf marker, interdimux path, leaf warning, zsh accents |
| green | `#a6d189` | green | 7.10:1 | success: leaf H2/tips, zsh ❯, colorls exec files |
| aqua | `#81c8be` | = teal | 6.41:1 | zsh cwd, web prompt_dir, colorls links |
| blue | `#8caaee` | blue | 5.34:1 | info: fzf info, interdimux ssh, leaf H3/links |
| purple | `#ca9ee6` | = mauve | 5.60:1 | fzf spinner, interdimux git badge, leaf H4/LaTeX |
| pink | `#f4b8e4` | pink | 7.52:1 | THE UI accent: tmux active border/❯/current match, fzf border, zsh branch, leaf brand |
| peach | `#ef9f76` | peach (= orange) | 5.80:1 | colorls hour_old — the contract allows peach to alias orange; catppuccin has no second mid warm |
| terracotta | `#ea999c` | = maroon | 5.59:1 | fzf pointer: the most saturated warm that is neither the peach nor the red, so the pointer stays distinct from hl/prompt |
| maroon | `#ea999c` | maroon | 5.59:1 | nvim parameters (identity) |

### Text ladder

| Token | Value | Origin | Contrast on bg | Role |
|-------|-------|--------|----------------|------|
| fg_primary | `#c6d0f5` | = text | 8.06:1 | fzf fg/query, interdimux query, colorls report |
| fg_secondary | `#b5bfe2` | = subtext1 | 6.75:1 | fzf label, colorls normal |
| fg_muted | `#a5adce` | = subtext0 | 5.55:1 | leaf inactive TOC entries, colorls file_small |
| fg_dim | `#949cbb` | = overlay2 | 4.53:1 | tmux status text/inactive borders, fzf header, colorls no_access. `overlay1` (3.65) would still clear every fg_dim floor (nested-off status 3.22 on panel_inset, floor 3.0) but drops tmux's status text below gruvbox-dark's own 4.14; overlay2 keeps it at 4.53 |
| fg_faint | `#6d738d` | **synthesised**: overlay0 mixed 35 % toward surface2 | 2.63:1 | zsh comments, interdimux tree, colorls tree, leaf soft lines and search-highlight bg. `overlay0` itself leaves body text on leaf's search highlight at 2.81 (floor 3.0) and `surface2` leaves zsh comments at 2.23 (floor 2.59); this is the band that clears both (3.06 / 2.63) |
| fg0 | `#c6d0f5` | = text | 8.06:1 | leaf body — the same text nvim and the terminal use |
| fg1 | `#f2d5cf` | = rosewater | 8.91:1 | leaf emphasis (bold, active TOC, marks) — frappe's brightest neutral, today's leaf identity, and the only value that keeps `<mark>` text above 3.5:1. Chosen over the literal gruvbox pairing (subtext1 body / text emphasis) because catppuccin's `text` *is* its body colour |

### Surfaces (dark ordering: bg_abyss < bg_deep < bg_primary < panel_inset < panel < panel_raised < border)

| Token | Value | Origin | Role |
|-------|-------|--------|------|
| bg_primary | `#303446` | = base | terminal/editor background (= ghostty "Catppuccin Frappe") |
| bg_deep | `#292c3c` | = mantle | leaf TOC/status bar, nvim NvimTree/Noice |
| bg_abyss | `#232634` | = crust | nvim Telescope/NoicePopup |
| panel_inset | `#383c50` | **synthesised**: mix(surface0, base, 50) | tmux menu/mode/message bg, interdimux current row. Catppuccin has no step between base and surface0; the midpoint is 1.13:1 on base and 1.15:1 under surface0 |
| panel | `#414559` | = surface0 | fzf selected row, leaf chips (badges, inline code, active TOC row) — leaf's chip today. `surface1` would drop inline code (teal) to 3.73:1 and fzf's hl to 3.37. fzf's hl on this chip is 4.45 (floor 4.5, within the audit's rounding — see exceptions) |
| panel_raised | `#51576d` | = surface1 | (nvim surface2 is identity, so vocabulary only) |
| border | `#737994` | = overlay0 | fzf separator/scrollbar, interdimux separator/border, leaf rules/heading underline/table separators — nvim's comment colour (`fields.comment = overlay0`, the contract's own slot for `border`) and the leaf rule / fzf separator colour the theme had before the contract; 2.87:1 on base. Unlike gruvbox (border 1.67 < faint 2.59) it sits above `faint` (2.63); `surface2` (2.23) would keep gruvbox's relation but regress the established line colour |

### Greys

| Token | Value | Origin | Role |
|-------|-------|--------|------|
| grey0 | `#838ba7` | = overlay1 | darkest of the triple (vocabulary) |
| grey1 | `#949cbb` | = overlay2 | leaf chrome text, zsh git punctuation/venv/jobs. zsh's floor is gruvbox's 4.02:1; overlay1 gives 3.65 |
| grey2 | `#a5adce` | = subtext0 | lightest of the triple (vocabulary) |

## Contract tokens — latte (light)

Latte's accents sit at 2.1–4.8:1 on `base` — catppuccin's light flavour is pastel by design. The editor keeps them (`ctp:`); every terminal-facing contract accent that misses its floor is the latte hue darkened with the pipeline's own `darken()` (HLS lightness points), stepped to the first value that clears every consumer's floor — the same treatment tokyonight-day, nord-light and onelight give their terminals.

### Accents

| Token | Value | Origin | Contrast on bg | Role / reason |
|-------|-------|--------|----------------|---------------|
| red | `#d20f39` | = ctp.red | 4.80:1 | clears its 4.26 floor as it is |
| orange | `#c64a10` | **darken(ctp.peach, 24)** | 4.23:1 | raw peach is 2.12; this clears fzf hl/prompt + interdimux accent (floor 3.76), tmux menus/copy-mode on panel_inset (3.62, floor 3.24) and fzf's hl on the chip (3.10, floor 2.93) |
| yellow | `#b27117` | **darken(ctp.yellow, 10)** | 3.53:1 | raw yellow is 2.31; floor 3.49 (tmux prefix flag, zsh accents, fzf marker, colorls sizes); crust reads 3.01 on it for the copy-mode match (floor 3.01) |
| green | `#338022` | **darken(ctp.green, 8)** | 4.37:1 | raw green is 2.96; floor 4.24 (zsh ❯, interdimux editor/success, colorls) — the green leaf already painted for its text roles |
| aqua | `#13797e` | **darken(ctp.teal, 6)** | 4.57:1 | raw teal is 3.31; zsh's cwd and colorls links need gruvbox-light's 4.36 |
| blue | `#145ff5` | **darken(ctp.blue, 2)** | 4.66:1 | raw blue is 4.34, 0.16 short of the 4.5 floor (fzf info, interdimux ssh, leaf H3, colorls) |
| purple | `#8839ef` | = ctp.mauve | 4.79:1 | clears the 4.44 floor as it is |
| pink | `#d421a4` | **darken(ctp.pink, 21)** | 4.08:1 | THE UI accent as ink magenta (floor 3.9: tmux active window, zsh branch, colorls exec, leaf brand); crust reads 3.49 on it for the copy-mode current match (floor 3.37). nvim's accent stays the pastel `ctp.pink` |
| peach | `#b5472f` | = terracotta | 4.75:1 | colorls hour_old (floor 4.5): the contract lets peach alias terracotta; the pastel `ctp.peach` (2.12) is editor-only |
| terracotta | `#b5472f` | **darken(ctp.rosewater, 22)** | 4.75:1 | fzf pointer (floor 4.5): rosewater darkened lands on an actual terracotta, distinct from the crimson red and from the orange; maroon darkened to 4.5 is just another red |
| maroon | `#e64553` | = ctp.maroon | 3.48:1 | no terminal consumer; nvim reads `ctp.maroon` |

### Text ladder (light: fg_secondary is darker than fg_primary, as in gruvbox-light)

| Token | Value | Origin | Contrast on bg | Role / reason |
|-------|-------|--------|----------------|---------------|
| fg_primary | `#4c4f69` | = text | 7.06:1 | main text |
| fg_secondary | `#3b3d51` | **synthesised**: darken(text, 8) | 9.42:1 | fzf label, colorls normal, and `fg1`. Latte has no neutral below `text`, and the light rule wants the emphasis step darker than body |
| fg_muted | `#5c5f77` | = subtext1 | 5.53:1 | `subtext0` (4.06 on mantle) would drop leaf's inactive TOC entries below 4.5 |
| fg_dim | `#7c7f93` | = overlay2 | 3.49:1 | `overlay1` (2.83) is below tmux's 3.0 status-text floor |
| fg_faint | `#9ca0b0` | = overlay0 | 2.30:1 | catppuccin's comment grey; `overlay1` would leave body text on leaf's search highlight at 2.49 (floor 3.0) |
| fg0 | `#4c4f69` | = text | 7.06:1 | leaf body |
| fg1 | `#3b3d51` | = fg_secondary | 9.42:1 | leaf emphasis |

### Surfaces (light: bg_primary is the lightest; chrome and raised sides step down independently)

| Token | Value | Origin | On bg | Role / reason |
|-------|-------|--------|-------|---------------|
| bg_primary | `#eff1f5` | = base | 1.00 | page/terminal background (= ghostty "Catppuccin Latte") |
| bg_deep | `#e6e9ef` | = mantle | 1.08 | leaf chrome, nvim mantle |
| bg_abyss | `#dce0e8` | = crust | 1.17 | nvim crust |
| panel_inset | `#dce0e8` | = crust | 1.17 | tmux selection/menus, interdimux current row. crust sits at the base↔surface0 midpoint (`mix()` gives `#dee0e8`), the same near-coincidence gruvbox-light has between its panel_inset (`#eee0b7`) and bg_abyss (`#f0e2b6`) |
| panel | `#ccd0da` | = surface0 | 1.37 | fzf selected row, leaf chips. `surface1` would drop body text on the chip to 4.39 and inline LaTeX to 2.98 |
| panel_raised | `#bcc0cc` | = surface1 | 1.61 | vocabulary (nvim surface2 is identity) |
| border | `#acb0be` | = surface2 | 1.91 | hard lines; quieter than `faint` (2.30), as in gruvbox-light (1.51 vs 2.21). `overlay0` — frappe's border and nvim's comment colour — *is* latte's `fg_faint`, which would paint leaf's rules and code frames in one grey, so the pair is deliberately asymmetric here |

### Greys (ordered dark → light per polarity, so the triple is frappe's mirrored)

| Token | Value | Origin |
|-------|-------|--------|
| grey0 | `#6c6f85` | = subtext0 |
| grey1 | `#7c7f93` | = overlay2 (leaf chrome text, zsh git punctuation — floor 3.24, overlay1 gives 2.83) |
| grey2 | `#8c8fa1` | = overlay1 |

## Catppuccin palette mapping (nvim)

Identity. Every key names its own upstream colour from the colorscheme's `ctp:` map, so the table is the flavour palette itself; the only deviations from stock catppuccin.nvim are the two pinned tweaks.

```
Catppuccin key  →  ctp.<key>   →  frappe     latte
──────────────────────────────────────────────────
rosewater       →  rosewater   →  #f2d5cf    #dc8a78
flamingo        →  flamingo    →  #eebebe    #dd7878
pink            →  pink        →  #f4b8e4    #ea76cb
mauve           →  mauve       →  #ca9ee6    #8839ef
red             →  red         →  #e78284    #d20f39
maroon          →  maroon      →  #ea999c    #e64553
peach           →  peach       →  #ef9f76    #f28d5e   (latte: user tweak, upstream #fe640b)
yellow          →  yellow      →  #e5c890    #df8e1d
green           →  green       →  #a6d189    #40a02b
teal            →  teal        →  #81c8be    #179299
sky             →  sky         →  #99d1db    #04a5e5
sapphire        →  sapphire    →  #85c1dc    #209fb5
blue            →  blue        →  #8caaee    #1e66f5
lavender        →  lavender    →  #b4b5ee    #7287fd   (frappe: user tweak, upstream #babbf1)
text            →  text        →  #c6d0f5    #4c4f69
subtext1        →  subtext1    →  #b5bfe2    #5c5f77
subtext0        →  subtext0    →  #a5adce    #6c6f85
overlay2        →  overlay2    →  #949cbb    #7c7f93
overlay1        →  overlay1    →  #838ba7    #8c8fa1
overlay0        →  overlay0    →  #737994    #9ca0b0
surface2        →  surface2    →  #626880    #acb0be
surface1        →  surface1    →  #51576d    #bcc0cc
surface0        →  surface0    →  #414559    #ccd0da
base            →  base        →  #303446    #eff1f5
mantle          →  mantle      →  #292c3c    #e6e9ef
crust           →  crust       →  #232634    #dce0e8
```

Versus the gruvbox template (`rosewater→pink`, `flamingo→terracotta`, `sky→blue`, `sapphire→aqua`, `lavender→fg_secondary`, `subtext0→grey1`, …) this is a deliberate whole-block deviation: the family decision is that catppuccin's own syntax identity (sky operators, sapphire misc, lavender namespaces, flamingo special files …) is kept exactly. `fields` are the gruvbox lines verbatim, so `vim.g.colors` (lualine, bufferline, the custom highlights) maps `orange → peach`, `accent → pink`, `comment → overlay0`, `alt_fg → surface2` as it does for gruvbox.

## Light-theme derivation (latte)

What is pinned and what is derived:

- **Pinned raw under `ctp:`** (nvim identity): all 26 upstream values. Of the names the contract shares, only `red` (4.80:1) and `maroon` (no terminal consumer) also serve as the contract token unchanged; `blue` misses by 0.16 and `yellow`, `green`, `pink`, `peach` do not carry text on `#eff1f5` at all (2.1–3.0:1). Every neutral aliases except `fg_secondary` (= `fg1`), which is `darken(text, 8)`.
- **Derived** with `darken()`: `pink = darken(ctp.pink, 21) #d421a4`, `yellow = darken(ctp.yellow, 10) #b27117`, `green = darken(ctp.green, 8) #338022`, `blue = darken(ctp.blue, 2) #145ff5`, `orange = darken(ctp.peach, 24) #c64a10`, `aqua = darken(ctp.teal, 6) #13797e`, `terracotta = darken(ctp.rosewater, 22) #b5472f`, `fg_secondary = darken(text, 8) #3b3d51`. Each is the first step that clears every consumer of that token; the derivation is reproducible with the pipeline's own filter.
- **Aliased where a raw value passes**: `purple = mauve`, `peach = terracotta`.

The leaf and web `text_darken` maps then add the little extra depth the ink tokens still need where they are text on a chip or on the web's code-block ground:

| Map | Key | Points | Result | Why |
|-----|-----|--------|--------|-----|
| leaf | accent | 3 | ink pink → `#c71f9a` | 3.32:1 on the surface0 chip (floor 3.3 — the status search badge), 4.54 on bg |
| leaf | accent2 | 1 | ink teal → `#12757a` | 3.53:1 on the chip (floor 3.35) |
| leaf | warning, success | — (absent) | ink yellow 3.53 / 3.28 on bg / mantle (floors 3.49 / 3.23); ink green 4.37 as H2, 3.38 on the watch badge (floors 4.24 / 3.31) | the ink tokens already clear their floors |
| web | accent / accent2 / success / info / special / warning / danger | 5 / 2 / 3 / 2 / 1 / 7 / 1 | | minimum points that clear 4.5:1 outright on BOTH bg `#eff1f5` and bg_deep `#e6e9ef` (special 4.45 and danger 4.46 raw on bg_deep, so one point each; success 2 would sit at 4.50 on bg_deep, so three) |
| web | pane_active | 5 | ink pink → `#be1e93` | 4.55 on bg_deep as pane-title text |
| web | prompt_dir | 2 | aqua → `#127075` | 4.80 on bg_deep (raw aqua is 4.57 on bg but 4.25 on bg_deep) |
| web | select_fg | 6 | orange → `#aa3f0e` | 4.63 on the crust selection surface (5 gave 4.46, under the 4.5 floor) |

Frappe needs neither map: every dark accent clears AA on base and mantle.

## Other per-theme choices

| Key | frappe | latte |
|-----|--------|-------|
| `tmux.clock` | 218 (`#ffafd7`), nearest xterm-256 index to pink `#f4b8e4`, the UI accent (was 219 `#ffafff`, nearest to nothing in the palette) | 166 (`#d75f00`), nearest to orange `#c64a10` (was 13, a system colour) |
| `ipython.pygments_style` | `dracula` — no catppuccin style is installed; the closest dark style in hue (pastel pink keywords, mauve strings, cyan on a blue-grey ground); the old `monokai` is yellow/green-led | `paraiso-light` — the closest light style in hue (mauve keywords, teal strings, peach numbers, cyan functions); `friendly` (the old value) is generic blue/green |
| `ghostty.name` | `Catppuccin Frappe` (background `#303446` = base) | `Catppuccin Latte` (background `#eff1f5` = base) |
| `kitty` | empty — `/opt/dotfiles/kitty/catppuccin-frappe.conf` matches the theme name | empty — `catppuccin-latte.conf` matches |
| `leaf.syntax` | `base16-ocean.dark` | `base16-ocean.light` |
| `nvim.theme` | `frappe` | `latte` (`winblend` 15 → 0) |

zsh moved from 256-colour indexes (frappe `203/117/110/149/179/176`, latte the same but cyan `39`) to the palette hex roles gruvbox uses: `red $red$`, `cyan $aqua$`, `blue $grey1$`, `green $green$`, `yellow $yellow$`, `magenta $pink$`, `comment $fg_faint$`. colorls moved from CSS colour names to gruvbox's 29-key token mapping. interdimux, previously absent from both themes, is gruvbox's 15 keys verbatim. `tools.web.prompt_dir` is `$aqua$`.

## Accepted contrast exceptions

Floor = min(WCAG target, the same pair in the gruvbox theme of the same polarity). Every row below is pinned by an identity the brief fixes; none is leaf body text.

**frappe** (128/130 pairs at or above the floor — 127 outright, plus one within the audit's rounding, noted below the table)

| Pair | Ratio | Floor | Why it cannot move |
|------|-------|-------|--------------------|
| leaf mark: strong_fg on mark_bg (`#f2d5cf` on pink-tinted `#7e6985`) | 3.58 | 4.0 | the mark bg is `accent` (pink, the fixed UI identity) mixed into base; rosewater is already frappe's brightest neutral |
| leaf status error: danger on red-tinted bar (`#e78284` on `#463947`) | 4.09 | 4.26 | `red` is pinned for nvim; the tint is derived from it |

fzf's hl on the selected row (peach `#ef9f76` on surface0 `#414559`) is 4.45:1 against a 4.5 floor — 0.05 under gruvbox's 4.50, accepted within the audit's rounding rather than listed as LOW. Peach and surface0 are both pinned; `surface1` as the chip would drop it to 3.37, so surface0 is the closest the palette offers.

**latte** (130/130): none. The ink derivation above is what removed the 27 rows an all-upstream latte terminal would carry (pink 2.34, yellow 2.31, green 2.96, blue 4.34, peach 2.12 on base); the pastel values still paint the editor through `ctp:`. To put the terminal back on the raw pastels, alias the five tokens to their `ctp:` anchors in `colorschemes/catppuccin-latte.yml` (`pink: *ctp_pink`, `yellow: *ctp_yellow`, `green: *ctp_green`, `blue: *ctp_blue`, `peach: *ctp_peach`) and restore the maps that darkened them for leaf and the web (leaf accent 24, warning 10, success 8; web accent 26, success 10, info 4, warning 17, pane_active 26). Either way the terminal is an improvement over the pre-contract latte (zsh green was index 149 `#afd75f`, 1.46:1; tmux selection was pink on surface0, 1.71:1).

## Files

### Interdotensional
- `colorschemes/catppuccin-frappe.yml`, `colorschemes/catppuccin-latte.yml` — upstream palette under `ctp:` (anchored, read only by the nvim overrides) + contract tokens (aliases on frappe, ink derivations on latte), single source of truth
- `config/themes/catppuccin-frappe.yml`, `config/themes/catppuccin-latte.yml` — the gruvbox config shape with `$token$` refs; the pair differs only on name/polarity/pair, clock, pygments style, ghostty name, leaf syntax, the text_darken maps, nvim theme and comments

### Neovim
- `lua/ui/schemes/_gruvbox-material.lua` — catppuccin setup with colour overrides from `vim.g.catppuccin_overrides` (shared with gruvbox)

### Generated
- `output/nvim/globals.lua` — `vim.g.catppuccin_overrides` (the identity table)
- `output/nvim/colors.lua` — semantic colour mapper
- `output/colorls/dark_colors.yaml`, `output/colorls/light_colors.yaml` — file listing colours (hex); both render, frappe reads the dark file and latte (`DISPLAY_MODE=Light`) the light one
- `output/tmux/.tmux.conf` — theme, status, copy-mode and interdimux colours
- `output/zsh/theme.zsh-theme`, `output/zsh/interdot.zsh` — prompt colours (hex), comment colour
- `output/fzf/fzf-colors.sh` — fzf palette
- `output/leaf/theme.toml` — leaf markdown reader theme
- `output/web/interdot-theme.css` — both polarities, latte roles darkened per the web map
