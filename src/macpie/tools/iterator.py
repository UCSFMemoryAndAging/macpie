import collections
import itertools


def duplicate_indices(iterable):
    """Make an iterator that returns duplicate items from the ``seq`` along
    with the the indices of that item. ::

        >>> seq = ['a', 'b', 'c', 'b', 'd']
        >>> dups = duplicate_indices(seq)
        >>> next(dups)
        ('b', [1, 3])
    """

    tally = collections.defaultdict(list)

    for i, item in enumerate(iterable):
        tally[item].append(i)

    dups = ((item, idxs) for item, idxs in tally.items() if len(idxs) > 1)

    return dups


def filter_get_index(predicate, iterable):
    """Make an iterator that yields items of ``iterable`` for which
    ``predicate`` returns true, along with the index of that item.

    Returns an iterator of 2-tuples, where the first value is the item
    that returned true, and the second value is the index of that item.

        >>> seq = ['a', 'b', 3, 'b', 'd']
        >>> nums = filter_get_index(lambda x: isinstance(x, int), seq)
        >>> next(nums)
        (3, 2)
    """
    if predicate is None:
        predicate = bool
    for i, item in enumerate(iterable):
        if predicate(item):
            yield item, i


def filter_get_meta(predicates, iterable, meta=None, only_first=False):
    """Make an iterator from items of ``iterable`` for which one or more
    ``predicates`` returns true, along with the index of that item and
    optional meta information.

    Returns an iterator of tuples of length 3, where the first value is the
    item that returned true, second value is the index of that item, and the
    third value is the corresponding object in ``meta`` if specified,
    otherwise it is the predicate function itself.

        >>> seq = [1, "asdf", 3, None, "a", 5]
        >>> valid_values = filter_get_meta(lambda x: isinstance(x, int), seq)
        >>> next(nums)
        (3, 2)

    :param predicates: a list of Boolean-valued functions
    :param iterable:
    :param meta: a list of objects parallel to ``predicates``, where if a
                 predicate returns true, the corresponding object in this iterable
                 will also be returned in the return tuple. If the meta iterable
                 is longer than the predicates iterable, meta will be truncated;
                 if meta is shorter than predicates,
    :param only_first: Boolean indicating whether to constrain results to
                       the first predicate that returns true. Each item only matches predicate once
    """
    if meta is None:
        meta = [p.__name__ for p in predicates]
    else:
        meta = overlay(meta, predicates, constrain_to_top=True)

    iterator = zip(predicates, meta)
    already_filtered = []
    for predicate, meta_value in iterator:
        for item, i in filter_get_index(predicate, iterable):
            if only_first and i in already_filtered:
                continue
            else:
                yield item, i, meta_value
                if only_first:
                    already_filtered.append(i)


def overlay(bottom, top, predicate=None, constrain_to_top=False, fillvalue=None):
    """Overlay elements from ``top`` over ``bottom``.
    If ``predicate`` is specified, only overlay elements from top over elements
    in ``bottom`` for which ``predicate`` (for bottom) is true.

    An iterator of the result is returned.

        >>> bottom = [1, 2, None, 4, None, 6, 7]
        >>> top = [0, 0, 3, 0, 5, 0, 0]
        >>> result = overlay(bottom, top, lambda x: x is None)
        >>> list(result)
        [1, 2, 3, 4, 5, 6, 7]

    :param bottom: if predicate is true for an element, overlay corresponding element
                   from top (i.e. replace the element with the one from top)
    :param top: iterable to copy values from
    :param predicate: Boolean-valued function to test each element of bottom,
                      overlaying parallel values from top if true. If 'None' (default),
                      do not overlay any values from top.
    :param constrain_to_top: constrain values to top. if true and top is shorter than bottom, truncate bottom
    to match length of top; if top is longer than bottom, fill extra elements with fillvalue
    :param fillvalue:

    """
    if predicate is None:
        predicate = lambda x: False

    sentinel = object()
    bottom_iterator = iter(bottom)
    top_iterator = iter(top)

    while bottom_iterator:
        bottom_elem = next(bottom_iterator, sentinel)
        if bottom_elem is sentinel:
            if constrain_to_top:
                for top_elem in top_iterator:
                    yield fillvalue
                return
            else:
                return

        top_elem = next(top_iterator, sentinel)
        if top_elem is sentinel:
            if constrain_to_top:
                return
            yield bottom_elem
            for bottom_elem in bottom_iterator:
                yield bottom_elem
            return

        if predicate(bottom_elem):
            yield top_elem
        else:
            yield bottom_elem
