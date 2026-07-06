import pytest

from interdotensional.filters import darken, lighten, mix, strip_hash


def test_lighten_moves_toward_white():
    assert lighten("#000000", 50) == "#808080"
    assert lighten("#ffffff", 10) == "#ffffff"


def test_darken_moves_toward_black():
    assert darken("#ffffff", 50) == "#808080"
    assert darken("#000000", 10) == "#000000"


def test_lighten_darken_roundtrip_hue_preserved():
    out = darken(lighten("#ea6962", 10), 10)
    # HLS round-trips can drift by a point of rounding, no more.
    orig = int("ea6962", 16)
    result = int(out.lstrip("#"), 16)
    for shift in (16, 8, 0):
        assert abs(((orig >> shift) & 0xFF) - ((result >> shift) & 0xFF)) <= 2


def test_mix_midpoint():
    assert mix("#000000", "#ffffff", 50) == "#808080"


def test_mix_zero_and_full():
    assert mix("#123456", "#ffffff", 0) == "#123456"
    assert mix("#123456", "#ffffff", 100) == "#ffffff"


def test_strip_hash():
    assert strip_hash("#282828") == "282828"
    assert strip_hash("282828") == "282828"


def test_three_digit_hex_accepted():
    assert mix("#f00", "#f00", 50) == "#ff0000"


def test_invalid_hex_raises():
    with pytest.raises(ValueError, match="not a hex color"):
        lighten("nope", 10)
