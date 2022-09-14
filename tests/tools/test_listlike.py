import re

import pytest

from macpie import lltools


def test_chunks():
    l1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    chunk_size1 = 3

    chunks = lltools.chunks(l1, chunk_size=chunk_size1)

    assert next(chunks) == [1, 2, 3]
    assert next(chunks) == [4, 5, 6]
    assert next(chunks) == [7, 8, 9]
    assert next(chunks) == [10]

    # chunk_size defaults to 2-ish
    chunks = lltools.chunks(l1)
    assert next(chunks) == [1, 2, 3, 4, 5]
    assert next(chunks) == [6, 7, 8, 9, 10]


def test_common_members():
    l1 = [1, 2, 3, 1, 2, 3]
    l2 = [2, 3, 4]
    assert list(lltools.common_members(l1, l2)) == [2, 3]


def test_difference():
    l1 = [1, 2, 6, 8]
    l2 = [2, 3, 5, 8]
    assert lltools.difference(l1, l2) == [1, 6]


def test_filter_seq():
    seq = ["col1", "col2", "col3", "date", "misc", "col6"]
    with pytest.raises(TypeError):
        lltools.filter_seq(seq)

    assert lltools.filter_seq(seq, items=(), regex=None, like=None)[0] == []
    assert lltools.filter_seq(seq, items=["col7"])[0] == []
    assert lltools.filter_seq(seq, items=["col7"], invert=True)[0] == [
        "col1",
        "col2",
        "col3",
        "date",
        "misc",
        "col6",
    ]
    assert lltools.filter_seq(seq, regex="^albert")[0] == []
    assert lltools.filter_seq(seq, items=["col7"], regex="^albert")[0] == []
    assert lltools.filter_seq(seq, items=["col2", "col1"])[0] == ["col1", "col2"]
    assert lltools.filter_seq(seq, items=["col1", "col2"], invert=True)[0] == [
        "col3",
        "date",
        "misc",
        "col6",
    ]
    assert lltools.filter_seq(seq, like="ol")[0] == ["col1", "col2", "col3", "col6"]
    assert lltools.filter_seq(seq, like="ol", invert=True)[0] == ["date", "misc"]
    assert lltools.filter_seq(seq, regex="^da")[0] == ["date"]
    assert lltools.filter_seq(seq, regex="^col", invert=True)[0] == ["date", "misc"]
    assert lltools.filter_seq(seq, like="ol", regex="^da")[0] == [
        "col1",
        "col2",
        "col3",
        "date",
        "col6",
    ]
    assert lltools.filter_seq(seq, items=["col1", "misc"], like="ol", regex="^da")[0] == [
        "col1",
        "col2",
        "col3",
        "date",
        "misc",
        "col6",
    ]
    assert lltools.filter_seq(seq, pred=lambda x: x.startswith("co"))[0] == [
        "col1",
        "col2",
        "col3",
        "col6",
    ]


def test_filter_seq_with_sub_seqs():
    seq = [("CDR", "PIDN"), ("CDR", "DCDate"), ("CDR", "InstrID"), "RANDOM"]

    assert lltools.filter_seq(seq, items=[("CDR", "PIDN")])[0] == [("CDR", "PIDN")]
    assert lltools.filter_seq(seq, items=[("CDR", "PIDNS")])[0] == []
    assert lltools.filter_seq(seq, like="CD")[0] == [
        ("CDR", "PIDN"),
        ("CDR", "DCDate"),
        ("CDR", "InstrID"),
    ]
    assert lltools.filter_seq(seq, like="ID")[0] == [
        ("CDR", "PIDN"),
        ("CDR", "InstrID"),
    ]
    assert lltools.filter_seq(seq, regex=re.compile("id", re.IGNORECASE))[0] == [
        ("CDR", "PIDN"),
        ("CDR", "InstrID"),
    ]
    assert lltools.filter_seq(seq, regex=re.compile("id", re.IGNORECASE), invert=True)[0] == [
        ("CDR", "DCDate"),
        "RANDOM",
    ]
    assert lltools.filter_seq(seq, regex=re.compile("id$", re.IGNORECASE))[0] == [
        ("CDR", "InstrID")
    ]


def test_filter_seq_pair():
    left_seq = ["col1", "col2", "col3", "date", "misc1", "col6"]
    right_seq = ["col1", "col2", "col3", "date", "misc2", "col6"]

    assert lltools.filter_seq_pair(left_seq, right_seq, intersection=True) == (
        (["col1", "col2", "col3", "date", "col6"], ["col1", "col2", "col3", "date", "col6"]),
        (["misc1"], ["misc2"]),
    )

    assert lltools.filter_seq_pair(
        left_seq, right_seq, left_filter_seq_kwargs={"like": "col"}
    ) == (
        (["col1", "col2", "col3", "col6"], ["col1", "col2", "col3", "date", "misc2", "col6"]),
        (["date", "misc1"], []),
    )

    assert lltools.filter_seq_pair(left_seq, right_seq, regex="^col", invert=True) == (
        (["date", "misc1"], ["date", "misc2"]),
        (["col1", "col2", "col3", "col6"], ["col1", "col2", "col3", "col6"]),
    )

    assert lltools.filter_seq_pair(
        left_seq,
        right_seq,
        regex="^col",
        invert=True,
        intersection=True,
    ) == (
        (["date"], ["date"]),
        (["col1", "col2", "col3", "misc1", "col6"], ["col1", "col2", "col3", "misc2", "col6"]),
    )


def test_is_disjoint():
    l1 = [1, 2, 6, 8]
    l2 = [2, 3, 5, 8]
    assert lltools.is_disjoint(l1, l2) is False

    l1 = [1, 2, 3, 4]
    l2 = [5, 6, 7, 8]
    assert lltools.is_disjoint(l1, l2) is True


def test_is_list_like():

    l1 = ["a", "b", "c"]
    t1 = ("a", "b")

    assert lltools.is_list_like(l1) is True

    assert lltools.is_list_like(t1) is True

    assert lltools.is_list_like("nope") is False

    assert lltools.is_list_like({1, 2}, allow_sets=False) is False

    assert lltools.is_list_like({1, 2}, allow_sets=True) is True


def test_make_list_if_list_like():
    assert lltools.make_list_if_list_like("a") == "a"
    assert lltools.make_list_if_list_like(["a", "b"]) == ["a", "b"]
    assert lltools.make_list_if_list_like(("a", "b")) == ["a", "b"]


def test_make_tuple_if_list_like():
    assert lltools.make_tuple_if_list_like("a") == "a"
    assert lltools.make_tuple_if_list_like(["a", "b"]) == ("a", "b")
    assert lltools.make_tuple_if_list_like(("a", "b")) == ("a", "b")


def test_maybe_make_list():
    assert lltools.maybe_make_list("a") == ["a"]
    assert lltools.maybe_make_list(["a"]) == ["a"]
    assert lltools.maybe_make_list(("a",)) == ("a",)


def test_maybe_make_tuple():
    assert lltools.maybe_make_tuple("a") == ("a",)
    assert lltools.maybe_make_tuple(["a"]) == ["a"]
    assert lltools.maybe_make_tuple(("a", "b")) == ("a", "b")


def test_move_item_to():
    l1 = [0, 1, 2, 3, 4]
    # move item 0 to same position should do nothing
    lltools.move_item_to(l1, 1, 1)
    assert l1 == [0, 1, 2, 3, 4]

    l2 = [0, 1, 2, 3, 4]
    # move item 0 to where 3 is
    # test when item is before the new position
    lltools.move_item_to(l2, 0, 3)
    assert l2 == [1, 2, 0, 3, 4]

    l3 = [0, 1, 2, 3, 4]
    # move item 4 to where 3 is
    # test when item is after the new position
    lltools.move_item_to(l3, 4, 3)
    assert l3 == [0, 1, 2, 4, 3]

    l4 = ["c", "a", "b", "d", "e"]
    lltools.move_item_to(l4, "c", "d")
    assert l4 == ["a", "b", "c", "d", "e"]

    l5 = ["a", "b", "d", "e", "c"]
    lltools.move_item_to(l5, "c", "d")
    assert l5 == ["a", "b", "c", "d", "e"]

    l6 = ["a", "b", "d", "e", "c"]
    lltools.move_item_to(l6, "c", "c", offset=-1)
    assert l6 == ["a", "b", "d", "c", "e"]

    l7 = ["a", "b", "d", "e", "c"]
    lltools.move_item_to(l7, "c", "c", offset=-2)
    assert l7 == ["a", "b", "c", "d", "e"]

    l8 = ["a", "b", "d", "e", "c"]
    lltools.move_item_to(l8, "d", "c", offset=1)
    assert l8 == ["a", "b", "e", "c", "d"]


def test_list_like_str_equal():
    lltools.list_like_str_equal(["abc", "def"], ["abc", "def"], case_sensitive=True) is True

    lltools.list_like_str_equal(["abc", "def"], ["abc", "def"], case_sensitive=False) is True

    lltools.list_like_str_equal(["abc", "def"], ["ABC", "def"], case_sensitive=True) is False

    lltools.list_like_str_equal(["abc", "def"], ["ABC", "def"], case_sensitive=False) is True

    lltools.list_like_str_equal(["abc", "def"], ["ABC", "def", "g"], case_sensitive=False) is False

    lltools.list_like_str_equal(("abc", "def"), ("abc", "def"), case_sensitive=True) is True

    lltools.list_like_str_equal(("abc", "def"), ("abc", "def"), case_sensitive=False) is True

    lltools.list_like_str_equal(("abc", "def"), ("ABC", "def"), case_sensitive=True) is False

    lltools.list_like_str_equal(("abc", "def"), ("ABC", "def"), case_sensitive=False) is True

    lltools.list_like_str_equal(("abc", "def"), ("ABC", "def", "g"), case_sensitive=False) is False


def test_make_same_length():
    l1 = [1, 2, 3, None, None, None]
    l2 = [1, 2, 3, None]

    result = lltools.make_same_length(l1, l2)
    assert next(result) == tuple(l1)
    assert next(result) == tuple(l1)

    result = lltools.make_same_length(l2, l1)
    assert next(result) == tuple(l1)
    assert next(result) == tuple(l1)

    result = lltools.make_same_length(l1, l2, fillvalue=8)
    assert next(result) == tuple(l1)
    assert next(result) == (1, 2, 3, None, 8, 8)


def test_remove_duplicates():
    l1 = [1, 5, 2, 3, 2, 4, 3]

    l1_no_dups_order_preserved = [1, 5, 2, 3, 4]
    assert l1_no_dups_order_preserved == list(lltools.remove_duplicates(l1, preserve_order=True))

    l1_no_dups_order_not_preserved = [1, 2, 3, 4, 5]
    assert l1_no_dups_order_not_preserved == list(
        sorted(lltools.remove_duplicates(l1, preserve_order=False))
    )


def test_rtrim():
    l1 = [1, 2, 3, None, None]
    l1_result = lltools.rtrim(l1)
    assert list(l1_result) == [1, 2, 3]

    l2 = [1, 2, 3, None, None]
    l2_result = lltools.rtrim(l1, lambda x: x == 3)
    assert list(l2_result) == l2

    l3 = [1, 2, 3]
    l3_result = lltools.rtrim(l3)
    assert list(l3_result) == l3

    l4 = [1, 2, 3, 4, 4]
    l4_result = lltools.rtrim(l4, lambda x: x == 4)
    assert list(l4_result) == [1, 2, 3]


def test_rtrim_longest():

    l1 = [1, 2, 3, None, None, None]
    l2 = [1, 2, 3, None]

    result = lltools.rtrim_longest(l1, l2)
    assert len(result) == 2
    assert list(result[0]) == [1, 2, 3]
    assert list(result[1]) == [1, 2, 3]

    l1 = [1, 2, 3, None, None, None]
    l2 = [1, 2, None]

    result = lltools.rtrim_longest(l1, l2)
    assert list(result[0]) == [1, 2, 3]
    assert list(result[1]) == [1, 2, None]
