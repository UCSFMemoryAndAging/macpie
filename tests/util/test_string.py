import pytest

from macpie.util.string import add_suffix, strip_suffix


def test_add_suffix():
    assert add_suffix("testing", "suffix") == "testingsuffix"

    with pytest.raises(ValueError):
        add_suffix("test", "suffix", 5)

    with pytest.raises(ValueError):
        add_suffix("test", "suffix", 6)

    assert add_suffix("testing", "suffix", 7) == "tsuffix"

    assert add_suffix("testing", "suffix", 8) == "tesuffix"

    assert add_suffix("testing", "suffix", 9) == "tessuffix"


def test_strip_suffix():

    assert strip_suffix("test_y", "_y") == "test"

    assert strip_suffix(None, "_y") is None

    assert strip_suffix("hello", "_y") == "hello"
