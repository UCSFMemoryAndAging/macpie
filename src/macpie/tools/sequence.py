def chunks(a, n):
    """Generator yielding successive n-sized chunks from list ``a``. ::

        >>> list = [1, 2, 3, 4, 5, 6, 7]
        >>> chnks = chunks(list, 3)
        >>> next(chnks)
        [1, 2, 3]
        >>> next(chnks)
        [4, 5, 6]
        >>> next(chnks)
        [7]

    :param a: list
    :param n: size of chunks
    """
    for i in range(0, len(a), n):
        yield a[i:i + n]


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
    if is_list_like(a) and is_list_like(b):
        if len(a) == len(b):
            if case_insensitive:
                return str(a).lower() == str(b).lower()
            else:
                return str(a) == str(b)


def maybe_make_list(obj):
    """If ``obj`` is not list-like, return as a single item list.

    :param obj: obj to maybe make as a list

    :return: list
    """
    if obj is not None and not is_list_like(obj):
        return [obj]
    return obj


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
