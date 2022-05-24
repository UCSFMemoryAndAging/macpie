import functools

import pandas as pd

from macpie import itertools, lltools


def count_trailers(ser: pd.Series, predicates=None, count_na=True, count_empty_string=True):
    """
    Counts trailing elements in a :class:`pandas.Series` object for which
    each predicate in ``predicates`` returns True.

    Parameters
    ----------
    ser : Series
    predicates : single callable or list of callables, optional
        If this returns True for a trailing element, that element will be counted.
    count_na : bool, default True
        Whether to also count trailing elements that evaluate to True using
        :func:`pandas.isna()`
    count_empty_string : bool, default True
        Whether to also count trailing elements that are empty strings ``''``

    Returns
    -------
    int
        A count of trailing elements that match the predicate.

    Raises
    ------
    ValueError
        If `remove_na` is False and `remove_empty_string` is False and
        `predicates` is not specified.
    """

    final_predicates = []
    if predicates:
        predicates = lltools.maybe_make_list(predicates)
        final_predicates.extend(predicates)
    if count_na is True:
        final_predicates.append(lambda x: pd.isna(x))
    if count_empty_string:
        final_predicates.append(lambda x: x == "")

    if not final_predicates:
        raise ValueError(
            "At least one predicate must be specified if both 'count_na' and "
            "'count_empty_string' are False."
        )

    def combine_predicates_or(p1, p2):
        return lambda x: p1(x) or p2(x)

    final_single_predicate = functools.reduce(combine_predicates_or, final_predicates)

    counter = 0
    for val in reversed(ser.array):
        if final_single_predicate(val):
            counter += 1
        else:
            break

    return counter


def remove_trailers(ser: pd.Series, predicates=None, remove_na=True, remove_empty_string=True):
    """
    Removes trailing elements in a :class:`pandas.Series` object for which
    each predicate in ``predicates`` returns True.

    Parameters
    ----------
    ser : Series
    predicates : single callable or list of callables, optional
        If this returns True for a trailing element, that element will be removed.
    remove_na : bool, default True
        Whether to also remove trailing elements that evaluate to True using
        :func:`pandas.isna()`
    remove_empty_string : bool, default True
        Whether to also remove trailing elements that are empty strings ``''``

    Returns
    -------
    Series
        A Series of the result.

    Raises
    ------
    ValueError
        If `remove_na` is False and `remove_empty_string` is False and
        `predicates` is not specified.
    """

    count = count_trailers(
        ser, predicates=predicates, count_na=remove_na, count_empty_string=remove_empty_string
    )

    if count > 0:
        new_last_index = ser.size - count
        return ser.iloc[0:new_last_index]

    return ser


def rtrim(ser: pd.Series, trim_empty_string=True):
    """
    Trim trailing missing values from series.

    Parameters
    ----------
    ser : Series
    trim_empty_string : bool, default True
        Whether to also include empty strings when trimming.

        >>> ser = pd.Series([1, 2, 3, None, None])
        >>> rtrim(ser)
        0    1.0
        1    2.0
        2    3.0
        dtype: float64

    Returns
    -------
    Series
        Trimmed Series.
    """

    return remove_trailers(ser, remove_na=True, remove_empty_string=trim_empty_string)


def rtrim_longest(*sers, trim_empty_string=True, as_tuple=False):
    """
    Trim trailing missing values from each series. If the resulting series
    are of uneven length, missing values are filled with ``NaN`` values.

    Parameters
    ----------
    sers : Series objects
    trim_empty_string : bool, default True
        Whether to also include empty strings when trimming.
    as_tuple : bool, default False
        Whether to return the result as a tuple of Series instead of as a DataFrame.

    Returns
    -------
    DataFrame or tuple
        A DataFrame or tuple of Series, depending on ``as_tuple``.

    Examples
    --------
    >>> ser1 = pd.Series([1, "2", 3, "", None, None], name="ser1")
    >>> ser2 = pd.Series([1, "2", 3, "4", 5, 6], name="ser2")
    >>> rtrim_longest(ser1, ser2)
      ser1 ser2
    0    1    1
    1    2    2
    2    3    3
    3  NaN    4
    4  NaN    5
    5  NaN    6
    """

    result = []
    for ser in sers:
        result.append(rtrim(ser, trim_empty_string=trim_empty_string))

    if as_tuple:
        return tuple(result)
    return pd.concat(result, axis="columns")
