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


def make_same_length(*seqs, fillvalue=None):
    """Make sequences the same length, filling any shorter lists with
    ``fillvalue`` to make them equal-sized.

    Parameters
    ----------
    seqs : Sequences
    fillvalue : optional, default: None
        Value to fill missing items with (if ``seqs`` are of uneven length.)

    Returns
    -------
    Iterator
        An iterator that yields the resulting sequences.
    """

    max_len = len(max(seqs, key=len))
    for seq in seqs:
        seq = itertools.chain(seq, itertools.repeat(fillvalue, max_len - len(seq)))
        yield tuple(seq)


def make_tuple_if_list_like(obj, allow_sets: bool = True):
    if is_list_like(obj, allow_sets=allow_sets):
        return tuple(obj)
    return obj


def make_unique(
    seq,
    suffs_iter=None,
    suffs_prefix="",
    suffs_suffix="",
    skip=0,
    skip_suffix="",
    inplace=False,
):
    """Make sequence of string elements unique by adding a differentiating suffix.

    Parameters
    ----------
    seq : Sequence
        Mutable sequence of strings
    suffs_iter : optional, default is itertools.count(1)
        An alternative iterable of suffixes
    suffs_prefix : optional, default is empty string
        An alternative string to prepend to each suffix in ``suffs_iter``
    suffs_prefix : optional, default is empty string
        An alternative string to append to each suffix in ``suffs_iter``
    skip : optional, default is 0
        How many duplicates to skip before appending suffixes.
    skipped_suffix : optional, default is empty string
        Add this suffix to any skipped duplicates.
    inplace : optional, default is False
        Whether to modify the list in place

    Examples
    --------
    >>> lst = ["name", "state", "name", "city", "name", "zip", "zip"]
    >>> make_unique(lst)
    ["name1", "state", "name2", "city", "name3", "zip1", "zip2"]

    >>> make_unique(lst, skip=1)
    ["name", "state", "name1", "city", "name2", "zip", "zip1"]

    >>> make_unique(lst, suffs_prefix="_")
    ["name_1", "state", "name_2", "city", "name_3", "zip_1", "zip_2"]
    """

    if suffs_iter is None:
        suffs_iter = itertools.count(1)

    def final_suffs_iter():
        for si in suffs_iter:
            yield suffs_prefix + str(si) + suffs_suffix

    final_suffs_iter = itertools.chain(itertools.repeat(skip_suffix, skip), final_suffs_iter())

    if inplace:
        result = seq
    else:
        result = seq.copy()

    not_unique = [k for k, v in collections.Counter(result).items() if v > 1]
    suff_gens = dict(zip(not_unique, itertools.tee(final_suffs_iter, len(not_unique))))

    for idx, item in enumerate(seq):
        try:
            suffix = next(suff_gens[item])
        except KeyError:
            # s was unique
            continue
        else:
            result[idx] += suffix

    if inplace:
        return None
    return result


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

    Parameters
    ----------
    seqs : objects that are acceptable to the built-in :py:func:`reversed` function

    Examples
    --------
    >>> lst1 = [1, 2, 3, None, None]
    >>> lst2 = [1, 2, None, None]
    >>> trimmed = rtrim_longest(lst1, lst2)
    >>> list(trimmed[0])
    [1, 2, 3]
    >>> list(trimmed[1])
    [1, 2, None]
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
