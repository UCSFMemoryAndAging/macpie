import itertools
import string

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


def test_make_unique():
    l1 = ["name", "state", "name", "city", "name", "zip", "zip"]

    result = strtools.make_unique(l1)
    assert result == ["name1", "state", "name2", "city", "name3", "zip1", "zip2"]

    result = strtools.make_unique(l1, suffs_iter=itertools.count(2))
    assert result == ["name2", "state", "name3", "city", "name4", "zip2", "zip3"]

    result = strtools.make_unique(l1, suffs_iter=string.ascii_lowercase, suffs_prefix="_")
    assert result == ["name_a", "state", "name_b", "city", "name_c", "zip_a", "zip_b"]

    result = strtools.make_unique(l1, skip=1)
    assert result == ["name", "state", "name1", "city", "name2", "zip", "zip1"]

    result = strtools.make_unique(l1, skip=2)
    assert result == ["name", "state", "name", "city", "name1", "zip", "zip"]

    result = strtools.make_unique(l1, skip=2, skip_suffix="_skipped")
    assert result == [
        "name_skipped",
        "state",
        "name_skipped",
        "city",
        "name1",
        "zip_skipped",
        "zip_skipped",
    ]

    result = strtools.make_unique(l1, skip=3)
    assert result == ["name", "state", "name", "city", "name", "zip", "zip"]

    result = strtools.make_unique(l1, skip=3, skip_suffix="_skipped")
    assert result == [
        "name_skipped",
        "state",
        "name_skipped",
        "city",
        "name_skipped",
        "zip_skipped",
        "zip_skipped",
    ]

    result = strtools.make_unique(l1, suffs_prefix="_")
    assert result == ["name_1", "state", "name_2", "city", "name_3", "zip_1", "zip_2"]

    result = strtools.make_unique(l1, suffs_prefix="(", suffs_suffix=")")
    assert result == ["name(1)", "state", "name(2)", "city", "name(3)", "zip(1)", "zip(2)"]

    result = strtools.make_unique(l1, inplace=True)
    assert result is None
    assert l1 == ["name1", "state", "name2", "city", "name3", "zip1", "zip2"]

    l2 = [1, 2, 1, 3, 1, 4, 4]

    result = strtools.make_unique(l2, suffs_prefix="_")
    assert result == ["1_1", 2, "1_2", 3, "1_3", "4_1", "4_2"]


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
