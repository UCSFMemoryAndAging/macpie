from macpie import lltools


def test_chunks():
    l1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    n1 = 3

    chunks = lltools.chunks(l1, n1)

    assert next(chunks) == [1, 2, 3]
    assert next(chunks) == [4, 5, 6]
    assert next(chunks) == [7, 8, 9]
    assert next(chunks) == [10]


def test_is_list_like():

    l1 = ["a", "b", "c"]
    t1 = ("a", "b")

    assert lltools.is_list_like(l1) is True

    assert lltools.is_list_like(t1) is True

    assert lltools.is_list_like("nope") is False


def test_move():
    l1 = [0, 1, 2, 3, 4]
    # move item 0 to same position should do nothing
    lltools.move(l1, 1, 1)
    assert l1 == [0, 1, 2, 3, 4]

    l2 = [0, 1, 2, 3, 4]
    # move item 0 to where 3 is
    # test when item is before the new position
    lltools.move(l2, 0, 3)
    assert l2 == [1, 2, 0, 3, 4]

    l3 = [0, 1, 2, 3, 4]
    # move item 4 to where 3 is
    # test when item is after the new position
    lltools.move(l3, 4, 3)
    assert l3 == [0, 1, 2, 4, 3]

    l4 = ["c", "a", "b", "d", "e"]
    lltools.move(l4, "c", "d")
    assert l4 == ["a", "b", "c", "d", "e"]

    l5 = ["a", "b", "d", "e", "c"]
    lltools.move(l5, "c", "d")
    assert l5 == ["a", "b", "c", "d", "e"]


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
