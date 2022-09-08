import collections

_marker = object()


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


def filter_get_message(predicates, iterable, only_first=False):
    """Make an iterator from items of ``iterable`` for which one or more
    ``predicates`` returns true, along with the index of that item and
    optional message information.

    Returns an iterator of tuples of length 3, where the first value is the
    item that returned true, second value is the index of that item, and the
    third value is the corresponding object in ``meta`` if specified,
    otherwise it is the predicate function itself.

        >>> seq = [1, "asdf", 3, None, "a", 5]
        >>> valid_values = filter_get_message(lambda x: isinstance(x, int), seq)
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

    already_filtered = []
    for predicate in predicates:
        if callable(predicate):
            message = predicate.__name__
        else:
            try:
                predicate, message = predicate
            except TypeError:
                raise TypeError(
                    '"Predicate" should either be a callable or a length-2 sequence '
                    "where the first element is the predicate and the second element "
                    "is the message."
                )

        for item, i in filter_get_index(predicate, iterable):
            if only_first and i in already_filtered:
                continue
            else:
                yield i, item, message
                if only_first:
                    already_filtered.append(i)


def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns ``default``.

    If ``pred`` is not None, returns the first item
    for which ``pred(item)`` is true.

    Parameters
    ----------
    iterable :
    default : object, Default is False
        Default value if no true value found.
    pred : Boolean-valued function, Default is None

    Examples
    --------
    >>> mp.itertools.first_true([None, 0, 1])
    1
    >>> mp.itertools.first_true([None, 0, 1], pred=lambda x: x is not None)
    0
    >>> mp.itertools.first_true([None, 0, 1], pred=lambda x: x == 2)
    False
    >>> mp.itertools.first_true([None, 0, 1], pred=lambda x: x == 2, default='albert')
    'albert'

    Notes
    -----
    Taken from Itertools Recipes from https://docs.python.org/3/library/itertools.html
    """
    return next(filter(pred, iterable), default)


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

    Parameters
    ----------
    bottom : iterable
        if predicate is true for an element, overlay corresponding element
        from top (i.e. replace the element with the one from top)
    top : iterable
        iterable to copy values from
    predicate : Boolean-valued function
        to test each element of bottom,
        overlaying parallel values from top if true. If 'None' (default),
        do not overlay any values from top.
    constrain_to_top : bool, optional, default: False
        constrain values to top. if true and top is shorter than bottom, truncate bottom
        to match length of top; if top is longer than bottom, fill extra elements with fillvalue
    fillvalue : optional, default: None
        value to fill extra items with

    """
    if predicate is None:
        predicate = lambda x: False

    bottom_iterator = iter(bottom)
    top_iterator = iter(top)

    while bottom_iterator:
        bottom_elem = next(bottom_iterator, _marker)
        if bottom_elem is _marker:
            if constrain_to_top:
                for top_elem in top_iterator:
                    yield fillvalue
                return
            else:
                return

        top_elem = next(top_iterator, _marker)
        if top_elem is _marker:
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
