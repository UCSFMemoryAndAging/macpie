import functools
from typing import List

import numpy as np
import pandas as pd

import macpie.pandas as mppd
from macpie._config import get_option
from macpie.tools import lltools


def add_diff_days(
    df: pd.DataFrame, col_start: str, col_end: str, diff_days_col: str = None, inplace=False
):
    """
    Adds a column whose values are the number of days between ``col_start`` and ``col_end``

    Parameters
    ----------
    df : DataFrame
    col_start : str
        column containing the start date
    col_end : str
        column containing the end date
    diff_days_col: str, default=``mp.get_option('column.system.diff_days')``
        Give the added column a different name other than the default
    inplace : bool, default False
        Whether to add the column in place or return a copy

    Returns
    -------
    DataFrame
        A DataFrame of the result.
    """

    if diff_days_col is None:
        diff_days_col = get_option("column.system.diff_days")

    if col_start == col_end:
        raise KeyError("date columns have the same name: {col_start}=={col_end}")

    if not inplace:
        df = df.copy()

    df[diff_days_col] = df[col_end] - df[col_start]
    df[diff_days_col] = df[diff_days_col] / np.timedelta64(1, "D")

    if not inplace:
        return df


def any_duplicates(df: pd.DataFrame, col: str, ignore_nan: bool = False):
    """
    Return ``True`` if there are any duplicates in ``col``.

    Parameters
    ----------
    df : DataFrame
    col : str
        column to check for duplicates
    ignore_nan : bool, default False
        Whether to ignore ``nan`` values

    Returns
    -------
    bool
        True if there are duplicates, False otherwise.
    """

    col = mppd.get_col_name(df, col)
    if ignore_nan is True:
        return df[col].dropna().duplicated().any()
    return df[col].duplicated().any()


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


def is_date_col(df: pd.DataFrame, arr_or_dtype):
    """
    Check whether the provided array or dtype is of the datetime64 dtype.

    Parameters
    ----------
    df : DataFrame
    arr_or_dtype : array or dtype
    """
    return pd.api.types.is_datetime64_any_dtype(df[arr_or_dtype])


def mark_duplicates_by_cols(df: pd.DataFrame, cols: List[str]):
    """
    Create a column in ``df`` called ``get_option("column.system.duplicates")``
    which is a boolean Series denoting duplicate rows as identified by ``cols``.

    Parameters
    ----------
    df : DataFrame
    cols : list-like
        Only consider these columns for identifiying duplicates
    """
    df[get_option("column.system.duplicates")] = df.duplicated(subset=cols, keep=False)
    return df
