import itertools
import re

import pandas as pd

import macpie.core.common as com
from macpie.tools import itertools as mp_itertools, lltools, strtools


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
    a_set = set(a) if a is not None else set()
    b_set = set(b) if b is not None else set()

    return a_set.intersection(b_set)


def difference(a, b):
    """Return list of items in ``a`` that are not in ``b``,
    like ``a`` - ``b``, while preserving order. ::

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


def filter_seq(seq, items=None, like=None, regex=None, pred=None, invert=False):
    """
    Filter sequence of strings. The options ``items``, ``like``,
    and ``regex`` are additive and can be used in conjunction with one another.

    Parameters
    ----------
    seq : list-like of strings
        Sequence object to filter
    items : list-like
        Get elements from `seq` which are in `items`.
    like : str
        Get elements from `seq`` for which "`like` in `seq_element` == True".
    regex : str (regular expression)
        Get elements from `seq`` for which re.search(`regex`, `seq_element`) == True.
    pred : Boolean-valued function
        Get elements from `seq`` for which `pred`(`seq_element`) == True.
    invert : bool, default False
        Whether to invert the result (i.e. filter out elements returned by
        `items`, `like`, `regex`, or `pred`)

    Returns
    -------
    Tuple[List[str], List[int]]
        (filtered_elements, filtered_element_indexes)

    See Also
    --------
    filter_seq_pair
    """
    if list(seq) == []:
        return [], []

    nkw = com.count_not_none(items, like, regex, pred)
    if nkw == 0:
        raise TypeError("Must pass at least one of `items`, `like`, `regex`, or `pred`")

    def check_sub_seq(pred):
        def f(elem):
            if lltools.is_list_like(elem):
                for sub_elem in elem:
                    if pred(sub_elem):
                        return True
            else:
                if pred(elem):
                    return True
            return False

        return f

    result_idxs = []
    if items is not None:

        def items_pred(elem):
            return elem in items

        result_idxs += [idx for _, idx in mp_itertools.filter_get_index(items_pred, seq)]

    if like is not None:

        def like_pred(elem):
            return like in pd.core.dtypes.common.ensure_str(elem)

        result_idxs += [
            idx for _, idx in mp_itertools.filter_get_index(check_sub_seq(like_pred), seq)
        ]

    if regex is not None:

        def regex_pred(elem):
            return re.search(regex, pd.core.dtypes.common.ensure_str(elem)) is not None

        result_idxs += [
            idx for _, idx in mp_itertools.filter_get_index(check_sub_seq(regex_pred), seq)
        ]

    if pred is not None:
        result_idxs += [idx for _, idx in mp_itertools.filter_get_index(check_sub_seq(pred), seq)]

    result_idxs = list(remove_duplicates(result_idxs))
    result_idxs.sort()

    if invert:
        result_idxs = [idx for (idx, _) in enumerate(seq) if idx not in result_idxs]

    result_labels = [seq[idx] for idx in result_idxs]

    return result_labels, result_idxs


def filter_seq_pair(
    left, right, intersection=None, left_filter_seq_kwargs={}, right_filter_seq_kwargs={}, **kwargs
):
    """
    Filter pair of sequences of strings.

    Parameters
    ----------
    left : list-like of strings
        Left sequence to filter
    right : list-like of strings
        Right sequence to filter
    intersection : bool, default False
        Whether to only return the items common to both, after excluding
        any values filtered out by the \*filter_kwargs params.
    left_filter_seq_kwargs : dict
        Keyword arguments to pass to underlying :func:`filter_seq`
        to be applied to left sequences.
    right_filter_seq_kwargs : dict
        Keyword arguments to pass to underlying :func:`filter_seq`
        to be applied to right sequences.
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`filter_seq` function to be applied to both `left` and `right`.


    Returns
    -------
    Tuple[Tuple[str, str], Tuple[str, str]]
        ((left_items_kept, right_items_kept), (left_items_discarded, right_items_discarded))

    See Also
    --------
    filter_seq
    """
    left_items = []
    right_items = []

    if not kwargs or not any(kwargs.values()):
        # if no filtering is done, return all items
        if not left_filter_seq_kwargs:
            left_items = left
        if not right_filter_seq_kwargs:
            right_items = right
    else:
        left_items += filter_seq(left, **kwargs)[0]
        right_items += filter_seq(right, **kwargs)[0]

    if left_filter_seq_kwargs:
        left_items += filter_seq(left, **left_filter_seq_kwargs)[0]

    if right_filter_seq_kwargs:
        right_items += filter_seq(right, **right_filter_seq_kwargs)[0]

    if intersection:
        left_items = right_items = list(common_members(left_items, right_items))

    left_items_kept = filter_seq(left, items=left_items)[0]
    left_items_discarded = filter_seq(left, items=left_items_kept, invert=True)[0]
    right_items_kept = filter_seq(right, items=right_items)[0]
    right_items_discarded = filter_seq(right, items=right_items_kept, invert=True)[0]

    return ((left_items_kept, right_items_kept), (left_items_discarded, right_items_discarded))


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


def remove_duplicates(seq, preserve_order=True):
    """
    Remove duplicates from a sequence while preserving order.

    Parameters
    ----------
    seq : list-like
        Sequence to remove duplicates from
    preserve_order : bool, default is True
        If order does not need to be preserved, set to False
        for performance gains.
    """
    if preserve_order:
        return (key for key in dict.fromkeys(seq))
    else:
        return (item for item in set(seq))


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
