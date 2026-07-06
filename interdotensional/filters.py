"""Color-math Jinja2 filters.

Lets templates derive shades instead of palettes hand-maintaining every
variant::

    background {{ colors.bg_primary | darken(10) }}
    border     {{ colors.blue | mix(colors.bg_primary, 40) }}
    fg         {{ colors.fg_primary | strip_hash }}
"""

import colorsys


def _to_rgb(value: str) -> tuple[float, float, float]:
    digits = str(value).strip().lstrip("#")
    if len(digits) == 3:
        digits = "".join(c * 2 for c in digits)
    if len(digits) != 6:
        raise ValueError(f"not a hex color: {value!r}")
    return tuple(int(digits[i : i + 2], 16) / 255 for i in (0, 2, 4))


def _to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02x}" for c in rgb)


def lighten(value: str, percent: float) -> str:
    """Move a color's lightness up by ``percent`` points (HLS space)."""
    h, l, s = colorsys.rgb_to_hls(*_to_rgb(value))
    return _to_hex(colorsys.hls_to_rgb(h, min(1.0, l + percent / 100), s))


def darken(value: str, percent: float) -> str:
    """Move a color's lightness down by ``percent`` points (HLS space)."""
    h, l, s = colorsys.rgb_to_hls(*_to_rgb(value))
    return _to_hex(colorsys.hls_to_rgb(h, max(0.0, l - percent / 100), s))


def mix(value: str, other: str, percent: float = 50) -> str:
    """Blend ``percent``% of ``other`` into the color."""
    a, b = _to_rgb(value), _to_rgb(other)
    t = percent / 100
    return _to_hex(tuple(x * (1 - t) + y * t for x, y in zip(a, b)))


def strip_hash(value: str) -> str:
    """``#282828`` -> ``282828`` for formats that reject the leading hash."""
    return str(value).lstrip("#")


FILTERS = {
    "lighten": lighten,
    "darken": darken,
    "mix": mix,
    "strip_hash": strip_hash,
}
