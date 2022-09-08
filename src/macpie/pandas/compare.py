import pandas as pd

import macpie.pandas as mppd
from macpie._config import get_option
from macpie.tools import lltools


def compare(
    left: pd.DataFrame,
    right: pd.DataFrame,
    filter_kwargs={},
    **kwargs,
):
    """
    Compare to another DataFrame and show the differences.

    Parameters
    ----------
    left : DataFrame
        DataFrame to compare.
    right : DataFrame
        DataFrame to compare with.
    filter_kwargs : dict, optional
        Keyword arguments to pass to underlying :meth:`macpie.pandas.subset_pair`
        to pre-filter columns before comparison.
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :meth:`pandas.DataFrame.compare` method.

    Returns
    -------
    DataFrame
        Showing differences.
    """
    if filter_kwargs:
        (left, right) = mppd.subset_pair(left, right, **filter_kwargs)

    try:
        return left.compare(right, **kwargs)
    except ValueError:  # if dfs don't have identical labels or shape
        # first compare columns
        (left_only_cols, right_only_cols) = diff_cols(left, right)
        if left_only_cols or right_only_cols:
            col_diffs = pd.DataFrame()
            col_diffs["Left_Only_Cols"] = left_only_cols
            col_diffs["Right_Only_Cols"] = right_only_cols
            return col_diffs
        else:
            # then compare rows
            return diff_rows(left, right)


def diff_cols(left: pd.DataFrame, right: pd.DataFrame, filter_kwargs={}):
    """
    Find the column differences between two DataFrames.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    filter_kwargs : dict, optional
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels_pair`
        to pre-filter columns before comparison.

    Returns
    -------
    Length-2 tuple
        First element is the list of columns that exist only in ``left``,
        and second element is the list of columns that exist only in ``right``.
    """
    if filter_kwargs:
        ((left_cols, right_cols), _) = mppd.filter_labels_pair(left, right, **filter_kwargs)
    else:
        left_cols = left.columns
        right_cols = right.columns

    left_cols = list(lltools.remove_duplicates(left_cols))
    right_cols = list(lltools.remove_duplicates(right_cols))

    left_only_cols = lltools.difference(left_cols, right_cols)
    right_only_cols = lltools.difference(right_cols, left_cols)

    return (left_only_cols, right_only_cols)


def diff_rows(left: pd.DataFrame, right: pd.DataFrame, filter_kwargs={}):
    """
    If ``left`` and ``right`` share the same columns, returns a DataFrame
    containing rows that differ.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    filter_kwargs : dict, optional
        Keyword arguments to pass to underlying :meth:`macpie.pandas.subset_pair`
        to pre-filter columns before comparison.

    Returns
    -------
    DataFrame
    """
    if filter_kwargs:
        (left, right) = mppd.subset_pair(left, right, **filter_kwargs)

    left_cols = left.columns
    right_cols = right.columns

    if set(left_cols) == set(right_cols):
        indicator_col_name = get_option("column.system.prefix") + "_diff_rows_merge"
        if isinstance(left.columns, pd.MultiIndex) or isinstance(right.columns, pd.MultiIndex):
            # TODO: Doing a pd.merge() on MultiIndex dataframes with indicator
            # set to True/string resulted in the following error:
            # pandas.errors.PerformanceWarning: dropping on a non-lexsorted multi-index
            # without a level parameter may impact performance
            # Flatten the column MultiIndexes to get around this
            left.columns = left.columns.to_flat_index()
            right.columns = right.columns.to_flat_index()
        merged_df = pd.merge(left, right, indicator=indicator_col_name, how="outer")
        changed_rows_df = merged_df[merged_df[indicator_col_name] != "both"]
        return changed_rows_df

    raise KeyError("Dataframes do not share the same columns")


def equals(left: pd.DataFrame, right: pd.DataFrame, filter_kwargs={}):
    """
    For testing equality of :class:`pandas.DataFrame` objects

    Parameters
    ----------
    left : DataFrame
        left DataFrame to compare
    right : DataFrame
        right DataFrame to compare
    filter_kwargs : dict, optional
        Keyword arguments to pass to underlying :meth:`macpie.pandas.subset_pair`
        to pre-filter columns before comparison.

    Returns
    -------
    bool
        True if all elements, except those in filtered out columns,
        are the same in both objects, False otherwise.
    """
    if filter_kwargs:
        (left, right) = mppd.subset_pair(left, right, **filter_kwargs)
    return left.equals(right)
