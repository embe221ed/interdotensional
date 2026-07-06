"""Render colorscheme palettes as truecolor swatches in the terminal."""

import re

from .config import Project, load_colorscheme
from .tokens import flatten_dict

_HEX = re.compile(r"^#(?P<hex>[0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")


def _parse_hex(value) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    match = _HEX.match(value.strip())
    if not match:
        return None
    digits = match.group("hex")
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits)
    return tuple(int(digits[i : i + 2], 16) for i in (0, 2, 4))


def render_palette(project: Project, name: str, color: bool = True) -> str:
    """Return a printable swatch listing for one colorscheme."""
    palette = flatten_dict(load_colorscheme(project, name))
    width = max((len(token) for token in palette), default=0)
    lines = [name]
    for token, value in palette.items():
        rgb = _parse_hex(value)
        if color and rgb:
            r, g, b = rgb
            swatch = f"\x1b[48;2;{r};{g};{b}m      \x1b[0m"
        elif rgb:
            swatch = "      "
        else:
            # Not a hex color (unexpected in a palette) - flag it visibly.
            swatch = "  ??  "
        lines.append(f"  {swatch}  {str(value):<9} {token:<{width}}")
    return "\n".join(lines)
