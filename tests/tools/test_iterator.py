import pandas as pd

from macpie import itertools


def test_filter_get_index():
    seq = ["a", "b", 3, "b", "d"]
    nums = itertools.filter_get_index(lambda x: isinstance(x, int), seq)
    result = next(nums)

    assert result == (3, 2)


def test_filter_get_message():
    seq = [1, "asdf", 3, None, "a", 5]

    def blank_id(x):
        return x is None or pd.isnull(x)

    def invalid_num(x):
        return not isinstance(x, int)

    result = itertools.filter_get_message(
        [blank_id, invalid_num],
        seq,
        only_first=True,
    )
    assert list(result) == [
        (3, None, "blank_id"),
        (1, "asdf", "invalid_num"),
        (4, "a", "invalid_num"),
    ]

    result = itertools.filter_get_message(
        [(blank_id, "BLANK"), (invalid_num, "INVALID")],
        seq,
        only_first=True,
    )
    assert list(result) == [
        (3, None, "BLANK"),
        (1, "asdf", "INVALID"),
        (4, "a", "INVALID"),
    ]

    result = itertools.filter_get_message(
        [blank_id, invalid_num],
        seq,
        only_first=False,
    )
    assert list(result) == [
        (3, None, "blank_id"),
        (1, "asdf", "invalid_num"),
        (3, None, "invalid_num"),
        (4, "a", "invalid_num"),
    ]

    result = itertools.filter_get_message(
        [(blank_id, "BLANK"), (invalid_num, "INVALID")],
        seq,
        only_first=False,
    )
    assert list(result) == [
        (3, None, "BLANK"),
        (1, "asdf", "INVALID"),
        (3, None, "INVALID"),
        (4, "a", "INVALID"),
    ]


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
