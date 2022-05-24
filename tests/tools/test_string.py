import pytest

from macpie import strtools


def test_add_suffix():
    assert strtools.add_suffix("testing", "suffix") == "testingsuffix"

    with pytest.raises(ValueError):
        strtools.add_suffix("test", "suffix", 5)

    with pytest.raises(ValueError):
        strtools.add_suffix("test", "suffix", 6)

    assert strtools.add_suffix("testing", "suffix", 7) == "tsuffix"

    assert strtools.add_suffix("testing", "suffix", 8) == "tesuffix"

    assert strtools.add_suffix("testing", "suffix", 9) == "tessuffix"


def test_seq_contains():
    seq = ["Albert", "Lee"]

    assert strtools.seq_contains("Albert", seq) is True
    assert strtools.seq_contains("Nope", seq) is False
    assert strtools.seq_contains("albert", seq) is False
    assert strtools.seq_contains("albert", seq, case_sensitive=False) is True
    assert strtools.seq_contains("albertzzz", seq, case_sensitive=False) is False

    seq = ["Albert", None, False]
    assert strtools.seq_contains("Albert", seq, case_sensitive=False) is True


def test_strip_suffix():
    assert strtools.strip_suffix("test_y", "_y") == "test"

    assert strtools.strip_suffix(None, "_y") is None

    assert strtools.strip_suffix("hello", "_y") == "hello"


def test_str_equals():
    assert strtools.str_equals("ab", "AB", case_sensitive=True) is False

    assert strtools.str_equals("ab", "AB", case_sensitive=False) is True
