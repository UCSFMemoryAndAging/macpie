import pandas as pd

from macpie import itertools


def test_filter_get_index():
    seq = ["a", "b", 3, "b", "d"]
    nums = itertools.filter_get_index(lambda x: isinstance(x, int), seq)
    result = next(nums)

    assert result == (3, 2)


def test_filter_get_meta():
    seq = [1, "asdf", 3, None, "a", 5]
    result = itertools.filter_get_meta(
        [lambda x: x is None or pd.isnull(x), lambda x: not isinstance(x, int)],
        seq,
        meta=["Blank ID", "Invalid ID"],
        only_first=True,
    )
    assert list(result) == [
        (None, 3, "Blank ID"),
        ("asdf", 1, "Invalid ID"),
        ("a", 4, "Invalid ID"),
    ]

    seq = [1, "asdf", 3, None, "a", 5]
    result = itertools.filter_get_meta(
        [lambda x: x is None or pd.isnull(x), lambda x: not isinstance(x, int)],
        seq,
        meta=["Blank ID", "Invalid ID"],
        only_first=False,
    )
    assert list(result) == [
        (None, 3, "Blank ID"),
        ("asdf", 1, "Invalid ID"),
        (None, 3, "Invalid ID"),
        ("a", 4, "Invalid ID"),
    ]

    seq = [1, "asdf", 3, None, "a", 5]
    result = itertools.filter_get_meta(
        [lambda x: x is None or pd.isnull(x), lambda x: not isinstance(x, int)],
        seq,
        meta=None,
        only_first=False,
    )


def test_overlay_no_predicate():
    bottom = ["a", "b", "c"]
    top = [1, 2, 3, 4]
    expected_result = ["a", "b", "c"]
    result = itertools.overlay(bottom, top, predicate=None, constrain_to_top=False)
    assert list(result) == expected_result

    bottom = ["a", "b", "c"]
    top = [1, 2]
    expected_result = ["a", "b", "c"]
    result = itertools.overlay(bottom, top, predicate=None, constrain_to_top=False)
    assert list(result) == expected_result

    bottom = ["a", "b", "c"]
    top = [1, 2]
    expected_result = ["a", "b"]
    result = itertools.overlay(bottom, top, predicate=None, constrain_to_top=True)
    assert list(result) == expected_result

    bottom = ["a", "b", "c"]
    top = [1, 2, 3, 4]
    expected_result = ["a", "b", "c", "fill"]
    result = itertools.overlay(
        bottom, top, predicate=None, constrain_to_top=True, fillvalue="fill"
    )
    assert list(result) == expected_result

    bottom = [1, 2, None, 4, None, 6, 7, 8]
    top = [0, 0, 3, 0, 5, 0, 0]
    result = itertools.overlay(bottom, top, predicate=None, constrain_to_top=False)
    assert list(result) == bottom

    bottom = [1, 2, None, 4, None, 6, 7, 8]
    top = [0, 0, 3, 0, 5, 0, 0]
    expected_result = [1, 2, None, 4, None, 6, 7]
    result = itertools.overlay(bottom, top, predicate=None, constrain_to_top=True)
    assert list(result) == expected_result


def test_overlay_with_predicate():
    bottom = [1, 2, None, 4, None, 6, 7, 8]
    top = [0, 0, 3, 0, 5, 0, 0]
    result = itertools.overlay(bottom, top, predicate=lambda x: x is None, constrain_to_top=False)
    assert list(result) == [1, 2, 3, 4, 5, 6, 7, 8]

    bottom = [1, 2, None, 4, None, 6, 7, 8]
    top = [0, 0, 3, 0, 5, 0, 0]
    result = itertools.overlay(bottom, top, predicate=lambda x: x is None, constrain_to_top=True)
    assert list(result) == [1, 2, 3, 4, 5, 6, 7]

    bottom = [1, 2, None, 4, None, 6, 7, 8]
    top = [0, 0, 3, 0, 5, 0, 0, 0, 0, 0]
    result = itertools.overlay(
        bottom, top, predicate=lambda x: x is None, constrain_to_top=True, fillvalue="fill"
    )
    assert list(result) == [1, 2, 3, 4, 5, 6, 7, 8, "fill", "fill"]


def test_remove_duplicates():
    l1 = [1, 5, 2, 3, 2, 4, 3]

    l1_no_dups_order_preserved = [1, 5, 2, 3, 4]
    assert l1_no_dups_order_preserved == list(itertools.remove_duplicates(l1, preserve_order=True))

    l1_no_dups_order_not_preserved = [1, 2, 3, 4, 5]
    assert l1_no_dups_order_not_preserved == list(
        sorted(itertools.remove_duplicates(l1, preserve_order=False))
    )
