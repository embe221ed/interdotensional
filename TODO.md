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

- [ ] **Semantic token contract** — formalize a fixed palette vocabulary
  (bg ramp, fg ramp, semantic accents à la base16) so new themes fill ~20
  documented slots instead of mirroring existing files; would also enable
  importing base16/Gogh schemes via a small converter

- [ ] **Live terminal reload** — optional OSC 4/10/11 escape-sequence
  broadcast (or `kitty @ set-colors`) so open terminals recolor without
  restart; can be prototyped today as a hook
