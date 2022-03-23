import collections
import itertools

from . import string as strtools


def chunks(seq, chunk_size=None):
    """Make an iterator returning successive chunks of size ``chunk_size``
    from ``seq``. ::

        >>> list = [1, 2, 3, 4, 5, 6, 7]
        >>> chnks = chunks(list, 3)
        >>> next(chnks)
        [1, 2, 3]
        >>> next(chnks)
        [4, 5, 6]
        >>> next(chnks)
        [7]
    """

    if chunk_size is None:
        chunk_size = len(seq) // 2

    for i in range(0, len(seq), chunk_size):
        yield seq[i : i + chunk_size]


def common_members(a, b):
    a_set = set(a) if a else set()
    b_set = set(b) if b else set()

    return list(a_set.intersection(b_set))


def diff(a, b):
    """Return list of items in ``a`` that are not in ``b``,
    like ``a`` - ``b``. ::

        >>> l1 = [1, 2, 6, 8]
        >>> l2 = [2, 3, 5, 8]
        >>> l3 = diff(l1, l2)
        >>> l3
        [1, 6]

    :param a: list
    :param b: list
    """
    b = set(b)
    return [item for item in a if item not in b]


def is_disjoint(a, b):
    """Check if two lists are disjoint (i.e. have no element in common). ::

        >>> l1 = [1, 2, 6, 8]
        >>> l2 = [2, 3, 5, 8]
        >>> is_disjoint(l1, l2)
        False

    :param a: list
    :param b: list
    """
    a_set = set(a)
    b_set = set(b)
    if len(a_set.intersection(b_set)) > 0:
        return False
    return True


def is_list_like(obj, allow_sets: bool = True):
    """Whether ``obj`` is a tuple or list

    :param obj: object to check
    """
    if allow_sets:
        return isinstance(obj, (set, tuple, list))
    else:
        return isinstance(obj, (tuple, list))


def list_like_str_equal(a, b, case_sensitive=True):
    """Whether list of strings in ``a`` is equal to the list
    of strings in ``b``.

    :param a: list
    :param b: list
    :param case_insensitive: whether equality comparison should be case insensitive
    """
    if len(a) == len(b):
        for strs in zip(a, b):
            if not strtools.str_equals(strs[0], strs[1], case_sensitive=case_sensitive):
                return False
        return True
    return False


def make_list_if_list_like(obj, allow_sets: bool = True):
    if is_list_like(obj, allow_sets=allow_sets):
        return list(obj)
    return obj


def make_tuple_if_list_like(obj, allow_sets: bool = True):
    if is_list_like(obj, allow_sets=allow_sets):
        return tuple(obj)
    return obj


def maybe_make_list(obj, allow_sets: bool = True):
    """If ``obj`` is not list-like, return as a single item list.

    :param obj: obj to maybe make as a list

    :return: list
    """
    if obj is not None and not is_list_like(obj, allow_sets=allow_sets):
        return [obj]
    return obj


def maybe_make_tuple(obj, allow_sets: bool = True):
    """If ``obj`` is not list-like, return as a single item list.

    :param obj: obj to maybe make as a list

    :return: list
    """
    if obj is not None and not is_list_like(obj, allow_sets=allow_sets):
        return (obj,)
    return obj


def move_item_to(l, item, item_to_move_to, offset=0):
    """
    Move an item in a list to the just before the position of another item. ::

        >>> lst = ['c', 'a', 'b', 'd', 'e']
        >>> move_item_to(lst, 'c', 'd')
        >>> lst
        ['a', 'b', 'c', 'd', 'e']

    :param a: list
    :param item: list item to move
    :param item_to_move_to: ``item`` will be moved to the position just before this item
    """

    item_idx = l.index(item)
    item_to_move_to_idx = l.index(item_to_move_to)
    item_to_move_to_idx = item_to_move_to_idx + offset

    if item_idx < item_to_move_to_idx:
        l.insert(item_to_move_to_idx - 1, l.pop(item_idx))
    else:
        l.insert(item_to_move_to_idx, l.pop(item_idx))


def rtrim(seq, predicate=None):
    """
    Remove trailing elements from sequence as long as predicate is true.
    Return an iterator over the new sequence.

        >>> lst = [1, 2, 3, None, None]
        >>> trimmed = rtrim_seq(lst)
        >>> list(trimmed)
        [1, 2, 3]

    :param seq: an object acceptable to the built-in reversed function

    """
    if predicate is None:
        predicate = lambda x: x is None

    return reversed(tuple(itertools.dropwhile(predicate, reversed(seq))))


def rtrim_longest(*seqs, predicate=None, fillvalue=None):
    """
    Remove trailing elements from each sequence as long as predicate is true.
    If the resulting sequences are of uneven length, missing values are filled
    in with fillvalue.

        >>> lst1 = [1, 2, 3, None, None]
        >>> lst2 = [1, 2, None, None]
        >>> trimmed = rtrim_longest(lst1, lst2)
        >>> list(trimmed[0])
        [1, 2, 3]
        >>> list(trimmed[1])
        [1, 2, None]

    :param seq: an object acceptable to the built-in reversed function
    """

    if predicate is None:
        predicate = lambda x: x is None

    reversed_results = []
    max_len = 0
    for seq in seqs:
        seq = tuple(itertools.dropwhile(predicate, reversed(seq)))
        max_len = max(max_len, len(seq))
        reversed_results.append(seq)

    results = []
    for seq in reversed_results:
        seq = itertools.chain(reversed(seq), itertools.repeat(fillvalue, max_len - len(seq)))
        results.append(seq)

    return results
