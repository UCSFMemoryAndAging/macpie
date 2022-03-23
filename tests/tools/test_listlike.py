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
    assert lltools.common_members(l1, l2) == [2, 3]


def test_diff():
    l1 = [1, 2, 6, 8]
    l2 = [2, 3, 5, 8]
    assert lltools.diff(l1, l2) == [1, 6]


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


def make_list_if_list_like():
    assert lltools.make_list_if_list_like("a") == "a"
    assert lltools.make_list_if_list_like(["a", "b"]) == ["a", "b"]
    assert lltools.make_list_if_list_like(("a", "b")) == ["a", "b"]


def make_tuple_if_list_like():
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
