# tokyonight-storm / tokyonight-day themes

The **Tokyo Night** family on the gruvbox contract: `tokyonight-storm` (dark) keeps every upstream storm hex, `tokyonight-day` (light) keeps upstream day for everything the editor paints and carries darkened steps for what the terminal paints, and both render Neovim through the native **tokyonight.nvim** plugin.

## Design goals

- Match Ghostty's built-in "TokyoNight Storm" (`#24283b`) and "TokyoNight Day" (`#e1e2e7`) terminal backgrounds — terminal background == editor background == leaf page
- Keep every upstream tokyonight.nvim hex in the storm file and add the 28 contract tokens on top of them (YAML anchors, one hex per colour); the one upstream name a contract token repoints, `purple`, keeps its hex as `purple1`
- Keep the theme's established identities: `magenta2` as THE UI accent (tmux active border/❯, zsh branch, colorls exec, nvim accent), blue + magenta as the leaf brand pair, teal (`blue1`/`blue5`) for links and the cwd
- Give day a terminal palette that is at least as readable as gruvbox-material-light, pair by pair, without leaving tokyonight's hues: every darkened value is the upstream hue with its HLS lightness stepped down by the minimum that clears the floor
- Say, in the YAML, how every synthesised value was made and which floor it was made for

## Architecture

Both themes use **tokyonight.nvim natively** (`colorscheme: "tokyonight"`, `theme: storm` / `day`, `vanilla: false`). The plugin ships both polarities with equivalent integrations and the user's own tweaks live in `_tokyonight.lua` (`border_highlight`, Telescope, NvimTree, the day `Search` override), so the nvim block is the pre-contract one apart from two content-neutral edits — `fields` name tokyonight.nvim's own palette keys (`bg`, `fg`, `bg_dark`, `fg_gutter`, `comment`, `magenta`, `magenta2`, `blue1`, `blue5`, `bg_dark1`, `bg_highlight`) and nothing in the colorscheme YAML reaches the editor. There is no catppuccin key mapping for this family. The two edits are `scheme: "tokyonight"` (the template's default, spelled out so the block has gruvbox's shape; `globals.lua` renders the same line with or without it) and a re-indent of storm's `plugin:` block scalar to day's 2-space form so the pair diff is clean — the same Lua table, but `output/nvim/globals.lua` now renders it with 2-space inner indentation instead of the pre-contract 6-space, which Lua ignores.

Everything else follows the gruvbox shape: the two theme configs are copies of `gruvbox-material-dark.yml` / `-light.yml`; `diff config/themes/tokyonight-storm.yml config/themes/tokyonight-day.yml` touches only `name`, `polarity`, `pair`, `tmux.clock`, `ipython.pygments_style`, `ghostty.name`, `kitty.name`, `leaf.syntax`, the `text_darken` maps, `nvim.theme` and comments.

Per-theme choices the contract leaves open:

| key | storm | day | why |
|-----|-------|-----|-----|
| `tmux.clock` | `215` (`#ffaf5f`) | `94` (`#875f00`) | the nearest xterm-256 index to each theme's `orange` (`#ff9e64` / `#984f00`) |
| `ipython.pygments_style` | `material` | `friendly` | no tokyonight style is installed; `material` is the same Palenight lineage (blue-grey ground, purple keywords, blue functions, green strings — tokyonight's own syntax map); `friendly` is light and its navy functions / blue strings sit in day's ink-blue family and read on the grey page (paraiso-light's pastel strings wash out on `#e1e2e7`) |
| `ghostty.name` | `TokyoNight Storm` | `TokyoNight Day` | bundled themes whose `background` equals `bg_primary` |
| `kitty` | `name: "tokyonight_storm"` | empty | `/opt/dotfiles/kitty/tokyonight_storm.conf` exists under that stem; day's old `Tokyonight-Day` pointed at no file, so the block is empty and the template's default `<theme-name>.conf` applies |

## Color palette — tokyonight-storm (dark)

Upstream: folke/tokyonight.nvim `colors/storm.lua`, every hex kept — upstream `purple` `#9d7cd8` lives under `purple1`, because the contract `purple` is `magenta`. The names that are not contract tokens (`bg_dark`, `blue0`…`blue7`, `comment`, `cyan`, `dark3`, `dark5`, `fg_dark`, `fg_gutter`, `green1`, `green2`, `magenta`, `magenta2`, `purple1`, `red1`, `teal`, `terminal_black`, `neon_blue`, `git.*`) stay as upstream vocabulary; the contract tokens alias them.

### Accent colors

| Name | Hex | Origin | Contrast vs bg | Usage |
|------|-----|--------|----------------|-------|
| red | `#f7768e` | upstream red | 5.51:1 | Errors/danger: interdimux danger, leaf danger, zsh failed ❯, colorls dead_link/error/deletion |
| orange | `#ff9e64` | upstream orange | 7.16:1 | Warm secondary: tmux menu/mode/message text, fzf match + prompt, interdimux accent, colorls dir/file_large/untracked |
| yellow | `#e0af68` | upstream yellow | 7.28:1 | tmux prefix ●/zoomed window, fzf marker, interdimux path, leaf warning, zsh accents, colorls sizes |
| green | `#9ece6a` | upstream green | 7.97:1 | Strings/success: the zsh ❯, interdimux editor/success, leaf H2/tips, colorls executable |
| aqua | `#2ac3de` | = blue1 | 6.91:1 | cwd (zsh cyan, web prompt_dir), colorls links, leaf H3/links (`info`) — `teal` `#1abc9c` is greener and only 6.05:1 |
| blue | `#7aa2f7` | upstream blue | 5.78:1 | Info: fzf info, interdimux ssh, colorls files/user/inode, the leaf brand (`accent`) |
| purple | `#bb9af7` | = magenta | 6.30:1 | Numbers/git/special: fzf spinner, interdimux ‹branch›, colorls read/day_old, leaf H4/LaTeX + accent2 — see below |
| pink | `#ff007c` | = magenta2 | 3.84:1 | THE UI accent, the theme's identity: tmux active border/❯/window name/copy-mode current match, fzf border, zsh branch, colorls exec (see exceptions) |
| peach | = orange | | 7.16:1 | colorls hour_old (its value before the contract); tokyonight's only other warm is the salmon red |
| terracotta | = red | | 5.51:1 | Brand warm: fzf's pointer, which was red before the contract; `red1` `#db4b4b` is 3.55:1, under the pointer's 3.78 floor, and `orange` would make the pointer the same hex as fzf's hl/prompt |
| maroon | = red | | | Soft rose for nvim parameters — red *is* tokyonight's salmon; unused by the native engine |

`purple` is `magenta`, not upstream `purple` `#9d7cd8` (retained as `purple1`, which no consumer reads): magenta is tokyonight's keyword colour (the role catppuccin's mauve fills, and what the nvim block already maps `mauve` to), and upstream purple is 4.38:1 on the page and 3.46:1 on the chip — under the H4 (4.5), LaTeX-on-chip (4.23) and fzf/interdimux/colorls (4.5) floors. The cost is that leaf's `special` (H4, LaTeX) and `accent2` (H5+, inline code, TOC marker) share one colour in both polarities.

### Foreground scale

| Name | Hex | Origin | Contrast vs bg | Role |
|------|-----|--------|----------------|------|
| fg_primary | `#c0caf5` | fg | 9.02:1 | fzf fg/query, interdimux query, colorls report, leaf fg1 (bold) |
| fg_secondary | `#a9b1d6` | fg_dark | 6.90:1 | leaf body (fg0), colorls normal, fzf label — the white-vs-bright-white idiom leaf used before |
| fg_muted | `#8e96bc` | synthesised: mix(dark5, fg_dark, 50) | 5.02:1 (5.36 on bg_deep) | inactive TOC entries, colorls file_small; dark5 is 3.49:1 against a 4.5 floor |
| fg_dim | `#737aa2` | dark5 | 3.49:1 | tmux status text + pane borders (3.22:1 on the selection), fzf header, interdimux header, colorls no_access |
| fg_faint | `#545c7e` | dark3 | 2.23:1 | tree glyphs, leaf soft lines, zsh comments, colorls tree/no_modifier — body text reads 3.10:1 over it as leaf's search highlight (see exceptions) |

`fg_faint` is dark3 rather than `comment` `#565f89`: with fg_dark as the leaf body there is no grey that both clears the zsh comment floor (2.59 on bg) and keeps body text at 3.0 over it as the search highlight; dark3 is the upstream grey that protects the body-text pair and leaves only the chrome rows short.

### Background scale (aligned with Ghostty)

| Name | Hex | Origin | Contrast | Role |
|------|-----|--------|----------|------|
| bg_primary | `#24283b` | bg | — | Terminal, editor and leaf page (matches Ghostty "TokyoNight Storm") |
| bg_deep | `#1f2335` | bg_dark | 1.07:1 below bg | Chrome: leaf TOC + status bar, nvim sidebars/floats (`alt_bg`) |
| bg_abyss | `#1b1e2d` | bg_dark1 | 1.06:1 below bg_deep | Deepest: nvim `dark_bg` |
| panel_inset | `#292e42` | bg_highlight | 1.08:1 on bg | Selection surface: tmux menus/mode/message/popups, interdimux current row, nvim `light_bg` |
| panel | `#323852` | synthesised: mix(bg_highlight, fg_gutter, 50) | 1.26:1 on bg | Chips: fzf selected row, leaf badges/inline code/active TOC row |
| panel_raised | `#3b4261` | fg_gutter | 1.48:1 on bg | Raised step (nvim surface2 role; unused by the native engine) |
| border | `#414868` | terminal_black | 1.63:1 on bg | Hard lines: fzf separator/scrollbar, interdimux separator/border, leaf rules/heading underline/table separators |

tokyonight has one raised step (`bg_highlight`) and then jumps to the gutter grey, so the chip surface is the midpoint of the two: with `fg_gutter` as the chip, inline code (magenta) drops to 4.25:1 against a 4.5 floor. `terminal_black` and `blue7` are 1.03:1 apart, so only one of them can be a step; `terminal_black` is the neutral one and lands at gruvbox-dark's own border weight (1.63 vs 1.67). `panel_inset` sits at 1.08:1 — the audit's 1.1 floor within its rounding — because `bg_highlight` is the selection surface tmux already used.

### Grey scale

The three greys are the quiet neutrals the config draws with, ordered dark → light; tokyonight's blue-greys are polarity-specific, so they are chosen per theme (grey1 is the one with a floor: the zsh git punctuation, 4.02 dark / 3.24 light).

| Name | Hex | Origin | Role |
|------|-----|--------|------|
| grey0 | `#545c7e` | = fg_faint (dark3) | Darkest neutral (vocabulary only) |
| grey1 | `#8088af` | synthesised: mix(dark5, fg_dark, 25) | 4.20:1 — leaf dim (separators, shortcuts, code labels), zsh git punctuation; dark5 is 3.49:1 |
| grey2 | `#8e96bc` | = fg_muted | Lightest neutral (vocabulary only) |

## Color palette — tokyonight-day (light)

Sources: folke/tokyonight.nvim `colors/day.lua` (the published extras values), Ghostty "TokyoNight Day" (background `#e1e2e7`, foreground `#3760bf`). The six upstream accents the contract tokens take over are kept under an `upstream:` map in the colorscheme (no consumer reads it; it keeps them visible in `interdot preview`). Day's accents sit at 3.0–4.7:1 on its grey page and its ink-blue `fg` at 4.52:1 (3.99:1 on bg_deep), while zsh, colorls, fzf, interdimux and tmux have no `text_darken` map — so the six contract accents that share an upstream name (`red orange yellow green blue purple`) and the text ladder carry an HLS-darkened step of the upstream value, by the minimum that clears the gruvbox-light floor for that pair. Every other upstream name keeps its hex, and the editor (native tokyonight.nvim) keeps upstream day untouched.

### Accent colors

| Name | Hex | Origin | Contrast vs bg | Floor it was made for |
|------|-----|--------|----------------|-----------------------|
| red | `#b43737` | darken(red1 `#c64343`, 6) | 4.58:1 | zsh red / colorls / interdimux danger 4.26; fzf pointer 4.5 (terracotta = red). Upstream red `#f52a65` is 3.01:1, and darkening it to 4.5 lands next to pink `#d20065` (1.09:1 apart), so red1 is the base |
| orange | `#984f00` | darken(orange `#b15c00`, 5) | 4.70:1 (3.19:1 on the chip) | fzf match on the selected row 2.93, colorls hour_old 4.5 (peach = orange). Upstream is 3.69:1 / 2.51:1 |
| yellow | `#88693c` | darken(yellow `#8c6c3e`, 1) | 3.93:1 | tmux copy-mode match text on it 3.05 (floor 3.01; upstream 2.92); tmux/zsh/colorls yellow floors are 3.49 |
| green | `#536e36` | darken(green `#587539`, 2) | 4.45:1 | zsh ❯ / colorls / interdimux 4.24 (upstream 4.04) |
| aqua | `#006a83` | = blue5 | 4.79:1 | colorls link 4.36, leaf H3/links 4.5 — day's readable cyan (`cyan` 4.26:1, `blue1` 3.57:1) |
| blue | `#1561ca` | darken(blue `#2e7de9`, 11) | 4.52:1 | fzf info, interdimux ssh, colorls 4.5; the leaf brand (upstream 3.11:1) |
| purple | `#7141b4` | darken(purple `#7847bd`, 3) | 5.21:1 (3.54:1 on the chip) | leaf LaTeX on the chip 3.46 (upstream 3.21:1); also accent2, so inline code and the TOC marker |
| pink | `#d20065` | = magenta2 | 4.13:1 | THE UI accent, the theme's identity (the tmux/zsh/colorls floor is gruvbox-light's 3.9; see exceptions) |
| peach | = orange | | 4.70:1 | colorls hour_old |
| terracotta | = red | | 4.58:1 | fzf pointer — `red1` is 3.79:1 against the 4.5 floor, and `orange` would make the pointer the same hex as fzf's hl/prompt |
| maroon | = red | | | nvim parameters; unused by the native engine |

Day's leaf `danger` was `$red1$` before the contract because `$red$` washed out; the contract `red` *is* red1 darkened, so the deviation is gone. Day's leaf `accent2` was `$magenta2$` because `magenta` `#9854f1` (3.33:1) cannot carry chip text; under the contract `accent2` is `$purple$` in both polarities (= magenta on storm), so day's inline code is its darkened purple.

### Foreground scale

| Name | Hex | Origin | Contrast vs bg | Role |
|------|-----|--------|----------------|------|
| fg_secondary | `#203870` | darken(fg `#3760bf`, 20) | 8.72:1 | Emphasis: leaf fg1, colorls normal, fzf label |
| fg_primary | `#264284` | darken(fg, 15) | 7.40:1 (5.02:1 on the chip) | Body: leaf fg0, fzf fg/query, interdimux query, colorls report |
| fg_muted | `#535a7c` | darken(dark5 `#68709a`, 10) | 5.20:1 (4.58 on bg_deep) | inactive TOC entries, colorls file_small |
| fg_dim | `#68709a` | dark5 | 3.71:1 | tmux status text + pane borders (2.89:1 on the selection, floor 2.71), fzf header, interdimux header, colorls no_access |
| fg_faint | `#8990b3` | dark3 | 2.42:1 | tree glyphs, soft lines, zsh comments (floor 2.21); body text reads 3.05:1 over it as the search highlight |

Why the ink goes this dark: fzf's selected row, interdimux's current row and leaf's active TOC row all draw the raw body colour on the chip, and gruvbox-light's floor for those pairs is 4.5. Upstream `fg` is 3.07:1 on the chip and 1.87:1 over `fg_faint`; darken 12 clears the chip, but leaf's search highlight (body text over `fg_faint`, floor 3.0) needs darken 15. Emphasis is one clear step darker (gruvbox-light: 7.4 body / 9.6 bold; day: 7.4 / 8.7).

### Background scale (aligned with Ghostty)

| Name | Hex | Origin | Contrast | Role |
|------|-----|--------|----------|------|
| bg_primary | `#e1e2e7` | bg | — | Terminal, editor and leaf page (matches Ghostty "TokyoNight Day") |
| bg_deep | `#d0d5e3` | bg_dark | 1.13:1 below bg | Chrome: leaf TOC + status bar, nvim `alt_bg` |
| bg_abyss | `#c1c9df` | bg_dark1 | 1.13:1 below bg_deep | Deepest: nvim `dark_bg` |
| panel_inset | `#c4c8da` | bg_highlight | 1.29:1 on bg | Selection surface: tmux menus/mode/message, interdimux current row, nvim `light_bg` |
| panel | `#b6bbd2` | synthesised: mix(bg_highlight, fg_gutter, 50) | 1.47:1 on bg | Chips: fzf selected row, leaf badges/inline code/active TOC row |
| panel_raised | `#a8aecb` | fg_gutter | 1.69:1 on bg | Raised step (unused by the native engine) |
| border | `#a1a6c5` | terminal_black | 1.85:1 on bg | Hard lines |

The same four upstream names fill the same four slots in both polarities (`bg_highlight`, the synthesised midpoint, `fg_gutter`, `terminal_black`); `blue7` is 1.02:1 from `terminal_black` on day too, so it is skipped for the same reason.

### Grey scale

| Name | Hex | Origin | Role |
|------|-----|--------|------|
| grey0 | `#535a7c` | = fg_muted | Darkest neutral (vocabulary only) |
| grey1 | `#68709a` | dark5 (= fg_dim) | leaf dim, zsh git punctuation — 3.71:1 (floor 3.24) |
| grey2 | `#8990b3` | = fg_faint (dark3) | Lightest neutral (vocabulary only) |

### text_darken maps (day only)

leaf: `accent: 3` — the blue brand on the chip (status search badge) goes 3.07:1 → 3.43:1 (floor 3.3). Every other leaf role already sits at or above its floor raw, so `strong`, `success`, `warning` and `accent2` carry no point.

web (the roles that miss 4.5:1 on `bg` or `bg_deep` raw): `accent: 4`, `success: 3`, `info: 2`, `warning: 7`, `danger: 4`, `pane_active: 5`, `prompt_dir: 2`, `select_fg: 5`. Each is the smallest point that reaches 4.5:1 outright on both surfaces (one point lower lands at 4.32–4.49; `pane_active` at 3 cleared bg only, 4.11 on bg_deep); `prompt_dir` is the same aqua as `info` — 4.79:1 on bg raw but 4.22:1 on bg_deep — and carries the same 2. `fg`, `fg_strong`, `muted` and `accent2`/`special` (purple) pass on both surfaces without a point.

## Accepted contrast exceptions

All rows the audit still marks LOW, with the floor (min of the WCAG target and the same pair in the gruvbox theme of the same polarity). None is body text; every one is an upstream hex the contract or the brief told the family to keep.

| theme | pair | fg on bg | ratio | floor | why |
|-------|------|----------|-------|-------|-----|
| storm | tmux active window/accent: pink on bg | `#ff007c` on `#24283b` | 3.84 | 4.5 | `magenta2` is the theme's UI identity (`tools.tmux.colors.pink` before the contract); bold chrome glyphs and a 1-cell border |
| storm | tmux copy-mode current match: selection text on pink | `#292e42` on `#ff007c` | 3.54 | 4.5 | same hex, as a bold highlight background |
| storm | web pane_active (title text) on bg | `#ff007c` on `#24283b` | 3.84 | 4.5 | same hex; dark themes carry no web map |
| storm | zsh magenta (git branch) on bg | `#ff007c` on `#24283b` | 3.84 | 4.5 | same hex, bold |
| storm | colorls exec on bg | `#ff007c` on `#24283b` | 3.84 | 4.5 | same hex, the `x` bit |
| storm | zsh comment on bg | `#545c7e` on `#24283b` | 2.23 | 2.59 | `fg_faint` = dark3: no grey both clears 2.59 here and keeps fg_dark ≥ 3.0 over it as leaf's search highlight; the body-text pair wins (3.10) |
| storm | colorls no_modifier on bg | `#545c7e` on `#24283b` | 2.23 | 2.59 | same token (age column) |
| storm | colorls tree on bg | `#545c7e` on `#24283b` | 2.23 | 2.59 | same token (tree lines) |
| day | tmux copy-mode current match: selection text on pink | `#c4c8da` on `#d20065` | 3.21 | 3.37 | `magenta2` kept as the identity; every other day pink row clears its floor (4.13 vs 3.9) |

## Files

### Interdotensional
- `colorschemes/tokyonight-storm.yml`, `colorschemes/tokyonight-day.yml` — raw palettes (upstream vocabulary + the 28 contract tokens; single source of truth for every terminal target)
- `config/themes/tokyonight-storm.yml`, `config/themes/tokyonight-day.yml` — tool configs with `$token$` refs, copies of the gruvbox pair

### Neovim
- `lua/ui/schemes/_tokyonight.lua` — native tokyonight.nvim setup; reads the plugin's own palette, not the YAML

### Generated
- `output/nvim/globals.lua` — `vim.g.colorscheme` (name/scheme/theme/plugin spec); no `catppuccin_overrides`
- `output/nvim/colors.lua` — semantic mapper over tokyonight.nvim's palette keys
- `output/colorls/dark_colors.yaml` / `light_colors.yaml` — file listing colors (hex values; day renders the light file)
- `output/tmux/*` — clock, selection, pink/yellow/dim chrome, interdimux options
- `output/zsh/theme.zsh-theme` — prompt colors (truecolor hex, no more 256-colour indexes)
- `output/fzf/fzf-colors.sh` — the 13 gruvbox keys
- `output/leaf/theme.toml` — leaf markdown reader theme (role-driven via `tools.leaf`)
- `output/web/interdot-theme.css` — both polarities, day darkened by `tools.web.text_darken`
