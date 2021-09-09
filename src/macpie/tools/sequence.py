from collections import defaultdict
import itertools


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


def get_indices_of_duplicates(seq):
    """Make an iterator that returns duplicate items from the ``seq`` along
    with the the indices of that item. ::

        >>> seq = ['a', 'b', 'c', 'b', 'd']
        >>> dups = get_indices_of_duplicates(seq)
        >>> next(dups)
        ('b', [1, 3])
    """

    tally = defaultdict(list)

    for i, item in enumerate(seq):
        tally[item].append(i)

    dups = ((item, idxs) for item, idxs in tally.items() if len(idxs) > 1)

    return dups


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


def is_list_like(obj):
    """Whether ``obj`` is a tuple or list

    :param obj: object to check
    """
    return isinstance(obj, (tuple, list))


def list_like_str_equal(a, b, case_insensitive=False):
    """Whether list of strings in ``a`` is equal to the list
    of strings in ``b``.

    :param a: list
    :param b: list
    :param case_insensitive: whether equality comparison should be case insensitive
    """
    if is_list_like(a) and is_list_like(b) and len(a) == len(b):
        if case_insensitive:
            return str(a).lower() == str(b).lower()
        else:
            return str(a) == str(b)
    return False


def maybe_make_list(obj):
    """If ``obj`` is not list-like, return as a single item list.

    :param obj: obj to maybe make as a list

    :return: list
    """
    if is_list_like(obj):
        return list(obj)
    elif obj:
        return [obj]
    else:
        return []


def move(a, item, item_to_move_to):
    """
    Move an item in a list to the just before the position of another item. ::

        >>> lst = ['c', 'a', 'b', 'd', 'e']
        >>> move(lst, 'c', 'd')
        >>> lst
        ['a', 'b', 'c', 'd', 'e']

    :param a: list
    :param item: list item to move
    :param item_to_move_to: ``item`` will be moved to the position just before this item
    """
    item_idx = a.index(item)
    item_to_move_to_idx = a.index(item_to_move_to)

    if item_idx < item_to_move_to_idx:
        a.insert(item_to_move_to_idx - 1, a.pop(item_idx))
    elif item_idx > item_to_move_to_idx:
        a.insert(item_to_move_to_idx, a.pop(item_idx))


def remove_trailers(iterable, predicate=None):
    """
    Remove trailing elements from list as long as predicate is true.
    Return an iterator over the new list.
    """
    if predicate is None:
        predicate = lambda x: x is None

    return reversed(tuple(itertools.dropwhile(predicate, reversed(iterable))))
