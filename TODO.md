# TODO

## Features and Enhancements

- [x] **Symlink Management** — `interdot link` with a `links:` mapping in
  `config/general.yml` (dry-run, conflict backup via `--force`)

- [x] **Python Implementation Structure** — refactored into the
  `interdotensional/` package with a CLI, strict rendering, atomic writes,
  and a pytest suite

- [ ] **Neovim Theme Management**
  - ensure that the correct Neovim theme is installed
  - disable or remove any conflicting themes

- [x] **Semantic token contract** — the gruvbox pair's 28-token vocabulary
  (accents, fg ladder, surfaces, greys) is the contract every colorscheme
  fills, documented in `docs/theme-contract.md` and enforced by
  `tests/test_contract.py`; theme configs mirror the gruvbox config line for
  line. Still open: a base16/Gogh importer that fills the slots automatically

- [ ] **zellij themes block** — the zellij template only emits `theme "<name>"`;
  generate a `themes { <name> { … } }` block from the palette so every theme
  name resolves without a hand-written `~/.config/zellij/themes/<name>.kdl`

- [ ] **bat theme** — `~/.zshrc` hardcodes `BAT_THEME=gruvbox-*` by polarity;
  add a `tools.bat.theme` key (nord → Nord, onedarkpro → OneHalfDark/Light, …)
  and export it from `templates/zsh/interdot.zsh.j2`

- [ ] **Live terminal reload** — optional OSC 4/10/11 escape-sequence
  broadcast (or `kitty @ set-colors`) so open terminals recolor without
  restart; can be prototyped today as a hook
