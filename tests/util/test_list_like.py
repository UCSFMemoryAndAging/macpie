from macpie.util import is_list_like


def test_is_list_like():

    l1 = ['a', 'b', 'c']
    t1 = ('a', 'b')

    assert is_list_like(l1) is True

    assert is_list_like(t1) is True

    assert is_list_like("nope") is False
