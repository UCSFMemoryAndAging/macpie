import itertools
import re
from collections import defaultdict
from typing import List

import numpy as np
import pandas as pd

import macpie.core.common as com
from macpie._config import get_option
from macpie import lltools, strtools


def add_diff_days(
    df: pd.DataFrame, col_start: str, col_end: str, diff_days_col: str = None, inplace=False
):
    """
    Adds a column to DataFrame called ``_diff_days`` which contains
    the number of days between ``col_start`` and ``col_end``

    Parameters
    ----------
    df : DataFrame
    col_start : str
        column containing the start date
    col_end : str
        column containing the end date
    diff_days_col: str, optional
        Give the added column a different name other than the default
        name of "_diff_days".
    inplace : bool, default False
        Whether to add the column in place or return a copy.

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

    # df.assign(**{diff_days_col: (df[col_end] - df[col_start]) / np.timedelta64(1, "D")})
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

    col = get_col_name(df, col)
    if ignore_nan is True:
        return df[col].dropna().duplicated().any()
    return df[col].duplicated().any()


def assimilate(left: pd.DataFrame, right: pd.DataFrame):
    """
    Assimilate ``right`` to look like ``left`` by casting column data types in ``right``
    to the data types in ``left`` where the column name is the same.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame

    Returns
    -------
    DataFrame
        The assimilated ``right`` DataFrame
    """

    # give me all the elements in left that are also in right

    left_columns = set(left.columns)
    right_columns = set(right.columns)

    left_dtypes_dict = left.dtypes.to_dict()

    # find columns that are only in left but not in right
    left_only_cols = left_columns.difference(right_columns)
    for col in left_only_cols:
        del left_dtypes_dict[col]

    for col_name, dtype in left_dtypes_dict.items():
        try:
            right = right.astype({col_name: dtype})
        except pd.errors.IntCastingNaNError:
            pass

    return right


def compare(
    left: pd.DataFrame,
    right: pd.DataFrame,
    ignore_cols=None,
    left_ignore_cols=None,
    right_ignore_cols=None,
    cols_intersection=False,
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
    ignore_cols : list-like,
        Columns to ignore in either left or right DataFrame
    left_ignore_cols : list-like
        Columns to ignore in left DataFrame
    right_ignore_cols : list-like
        Columns to ignore in right DataFrame
    cols_intersection : bool, default False
        Whether to only compare the columns common to both, after
        ignoring any columns specifed in the *ignore_cols params.
    **kwargs
        All keyword arguments are passed through to the underlying
        :meth:`pandas.DataFrame.compare` method.

    Returns
    -------
    DataFrame
        Showing differences.
    """
    left_ignore_cols, right_ignore_cols = filter_labels_pair(
        left,
        right,
        ignore_cols=ignore_cols,
        left_ignore_cols=left_ignore_cols,
        right_ignore_cols=right_ignore_cols,
        cols_intersection=cols_intersection,
    )

    left = left.drop(columns=left_ignore_cols, errors="ignore")
    right = right.drop(columns=right_ignore_cols, errors="ignore")

    try:
        diffs = left.compare(right, **kwargs)
        if diffs.empty:
            return None
        return diffs
    except ValueError:  # if dfs don't have identical labels or shape
        # first compare columns
        (left_only_cols, right_only_cols) = left.mac.diff_cols(right)
        if left_only_cols != set() or right_only_cols != set():
            col_diffs = pd.DataFrame()
            col_diffs["Left_Only_Cols"] = list(left_only_cols)
            col_diffs["Right_Only_Cols"] = list(right_only_cols)
            return col_diffs

        # then compare rows
        else:
            row_diffs = left.mac.diff_rows(right)
            if row_diffs.empty:
                return None
            return row_diffs


def diff_cols(left: pd.DataFrame, right: pd.DataFrame, ignore_cols=None):
    """
    Find the column differences between two DataFrames.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    ignore_cols : list-like, optional
        Columns to ignore

    Returns
    -------
    Length-2 tuple
        First element is the set of columns that exist in ``left``,
        and the second element is the set of columns that only exist in ``right``.
    """
    if ignore_cols is None:
        ignore_cols = []
    else:
        ignore_cols = set(ignore_cols)

    left_columns = set(left.columns) - ignore_cols
    right_columns = set(right.columns) - ignore_cols

    left_only_cols = left_columns - right_columns
    right_only_cols = right_columns - left_columns

    return (left_only_cols, right_only_cols)


def diff_rows(left: pd.DataFrame, right: pd.DataFrame, ignore_cols=None):
    """
    If ``left`` and ``right`` share the same columns, returns a DataFrame
    containing rows that differ.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    ignore_cols : list-like, optional
        Columns to ignore

    Returns
    -------
    DataFrame
    """

    left = left.drop(columns=left_ignore_cols, errors="ignore")
    right = right.drop(columns=right_ignore_cols, errors="ignore")

    left = drop_cols(left, cols_list=cols_ignore, cols_pat=cols_ignore_pat)
    right = drop_cols(right, cols_list=cols_ignore, cols_pat=cols_ignore_pat)

    left_only_cols, right_only_cols = diff_cols(left, right)

    if left_only_cols == right_only_cols == set():
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


def drop_cols(df: pd.DataFrame, cols_list=set(), cols_pat="$^"):
    """
    Drop specified columns

    Parameters
    ----------
    df : DataFrame
    cols_list : list-like, optional
        List of columns to drop.
    cols_pat : Regular expression. Default is ``$^``
        Column names that match will be dropped. Default pattern is ``$^``
        which matches nothing so no columns are dropped.

    Returns
    -------
    DataFrame
        DataFrame with columns dropped.
    """

    if isinstance(df.columns, pd.MultiIndex):
        last_level = df.columns.nlevels - 1
        cols = df.columns.get_level_values(last_level)
    else:
        cols = df.columns

    cols_match_pat = cols.str.contains(cols_pat, regex=True)
    cols_to_keep = np.invert(cols_match_pat)

    df = df.loc[:, cols_to_keep]
    df = df.drop(columns=cols_list, errors="ignore")

    return df


def drop_suffix(df: pd.DataFrame, suffix):
    """
    Removes the ``suffix`` in any column name containing the ``suffix``.

    Parameters
    ----------
    df : DataFrame
    suffix : str
        suffix to drop

    Returns
    -------
    DataFrame
        DataFrame with renamed columns.
    """

    return df.rename(columns=lambda x: strtools.strip_suffix(x, suffix))


def equals(left: pd.DataFrame, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat="$^"):
    """
    For testing equality of :class:`pandas.DataFrame` objects

    Parameters
    ----------
    left : DataFrame
        left DataFrame to compare
    right : DataFrame
        right DataFrame to compare
    cols_ignore : list-like, optional
        DataFrame columns to ignore in comparison
    cols_ignore_pat: Regular expression. Default is ``$^``
        Column names that match will be ignored in comparison. Default pattern is ``$^``
        which matches nothing so no columns are ignored.

    Returns
    -------
    bool
        True if all elements, except those in ignored columns,
        are the same in both objects, False otherwise.

    Raises
    ------
    TypeError
        When columns are different types (e.g. Index vs MultiIndex)
    ValueError
        When MultiIndexes have different levels.
    """

    # columns should be same type (e.g. Index or MultiIndex)
    if type(left.columns) != type(right.columns):
        raise TypeError(
            f"Left columns type ('{type(left.columns)}') is "
            f"different than right columns type ('{type(right.columns)}')"
        )

    if isinstance(left.columns, pd.MultiIndex):
        if left.columns.nlevels != right.columns.nlevels:
            raise ValueError("MultiIndexes have different levels.")

    left = drop_cols(left, cols_list=cols_ignore, cols_pat=cols_ignore_pat)
    right = drop_cols(right, cols_list=cols_ignore, cols_pat=cols_ignore_pat)

    try:
        right = left.mac.assimilate(right)
    except NotImplementedError:
        pass

    return left.equals(right)


def filter_labels(
    *dfs: pd.DataFrame,
    items=None,
    like=None,
    regex=None,
    all_labels=None,
    invert=False,
    axis=None,
    level=None,
    result_level=None,
    result_type="single_list",
):
    """
    Filter dataframe row or column labels.

    Parameters
    ----------
    items : list-like
        Get labels from axis which are in `items`.
    like : str
        Get labels from axis for which "like in label == True".
    regex : str (regular expression)
        Get labels from axis for which re.search(regex, label) == True.
    all_labels : bool, default None
        If True, will get all labels from axis. The `level` parameter
        will be ignored.
    invert : bool, default False
        Whether to invert the result (i.e. discard labels returned by
        `items`, `like`, `regex`, or `all_labels`)
    axis : {0 or ‘index’, 1 or ‘columns’, None}, default None
        The axis to filter labels on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.
    level : str or int, optional
        For a MultiIndex, level (name or number) to use for
        filtering. Default is the highest level
    result_level : str or int, optional
        For a MultiIndex, return the labels at the requested
        level (name or number). Default is returning all levels.
    result_type : {'single_list', 'single_list_no_dups', 'list_of_lists'}, default 'single_list_no_dups'
        Indicates how results should be returned.
        * single_list: Results are flattened into a single list
        * single_list_no_dups: Results are flattened into a single list with duplicates removed
        * list_of_lists: List of lists.

    Returns
    -------
    List of labels. See ``result_type`` parameter.

    See Also
    --------
    DataFrame.filter : Subset the dataframe rows or columns according
    to the specified index labels.

    Notes
    -----
    The ``items``, ``like``, ``regex`` and ``all_labels``
    parameters are enforced to be mutually exclusive.
    ``axis`` defaults to the info axis that is used when indexing
    with ``[]``.
    """

    if result_type not in ["single_list", "single_list_no_dups", "list_of_lists"]:
        raise ValueError(
            "invalid value for result_type, must be one "
            "of {'single_list', 'single_list_no_dups', 'list_of_lists'}"
        )

    if all_labels is not True:
        all_labels = None

    nkw = com.count_not_none(items, like, regex, all_labels)
    if nkw > 1:
        raise TypeError(
            "Keyword arguments `items`, `like`, `not_like` and `all_labels` are mutually exclusive"
        )

    if axis is None:
        axis = dfs[0]._info_axis_name

    final_result = []
    for df in dfs:
        labels = df._get_axis(axis)

        mi_labels = None
        if isinstance(labels, pd.MultiIndex):
            if level is None:
                mi_level = labels.nlevels - 1
            else:
                mi_level = level
            mi_labels = labels.copy()
            labels = mi_labels.get_level_values(mi_level)

        if all_labels is not None:
            result_idxs = list(range(len(labels)))
        elif items is not None:
            result_idxs = [idx for (idx, label) in enumerate(labels) if label in items]
        elif like:
            result_idxs = [
                idx
                for (idx, label) in enumerate(labels)
                if like in pd.core.dtypes.common.ensure_str(label)
            ]
        elif regex:
            result_idxs = [
                idx
                for (idx, label) in enumerate(labels)
                if re.search(regex, pd.core.dtypes.common.ensure_str(label)) is not None
            ]
        else:
            raise TypeError("Must pass either `items`, `like`, `regex`, or `all_labels`")

        if invert:
            result_idxs = [idx for (idx, _) in enumerate(labels) if idx not in result_idxs]

        if mi_labels is not None:
            result = [mi_labels[idx] for idx in result_idxs]
            if result_level is not None:
                result_level = mi_labels._get_level_number(result_level)
                result = list(list(zip(*result))[result_level])
        else:
            result = [labels[idx] for idx in result_idxs]

        final_result.append(result)

    if result_type == "single_list" or result_type == "single_list_no_dups":
        final_result = list(itertools.chain.from_iterable(final_result))
        if result_type == "single_list_no_dups":
            final_result = lltools.remove_duplicates(final_result)

    return final_result


def filter_labels_pair(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_filter_labels_kwargs={},
    right_filter_labels_kwargs={},
    both_filter_labels_kwargs={},
    labels_intersection=None,
):
    """
    Filter row or column labels of a pair of dataframes.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    left_filter_labels_kwargs : dict
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels`
        to be applied to left DataFrame.
    right_filter_labels_kwargs : list-like
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels`
        to be applied to right DataFrame.
    both_filter_labels_kwargs : list-like
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels`
        to be applied to both DataFrames.
    labels_intersection : bool, default False
        Whether to only return the labels common to both, after
        filtering any labels specifed in the *filter_labels_kwargs params.

    Returns
    -------
    Length-2 Tuple of Length-2 Tuples
        ((left_labels_returned, left_labels_discarded), (right_labels_returned, right_labels_discarded))
    """
    nkw = com.count_bool_true(
        left_filter_labels_kwargs,
        right_filter_labels_kwargs,
        both_filter_labels_kwargs,
        labels_intersection,
    )

    if nkw == 0:
        raise TypeError(
            "Must pass at least one of `left_filter_labels_kwargs`, "
            "`right_filter_labels_kwargs`, `both_filter_labels_kwargs`, or `labels_intersection`"
        )

    left_labels = (
        [] if not left_filter_labels_kwargs else filter_labels(left, **left_filter_labels_kwargs)
    )
    right_labels = (
        []
        if not right_filter_labels_kwargs
        else filter_labels(right, **right_filter_labels_kwargs)
    )
    if both_filter_labels_kwargs:
        left_labels += filter_labels(left, **both_filter_labels_kwargs)
        right_labels += filter_labels(right, **both_filter_labels_kwargs)

    # if no filtering is done, return all labels
    if not left_filter_labels_kwargs and not both_filter_labels_kwargs:
        left_labels = filter_labels(left, all_labels=True)
    if not right_filter_labels_kwargs and not both_filter_labels_kwargs:
        right_labels = filter_labels(right, all_labels=True)

    if labels_intersection:
        common_labels = lltools.common_members(left_labels, right_labels)
        left_labels = common_labels
        right_labels = common_labels

    left_keep_labels = filter_labels(left, items=left_labels)
    left_ignore_labels = filter_labels(left, items=left_labels, invert=True)
    right_keep_labels = filter_labels(right, items=right_labels)
    right_ignore_labels = filter_labels(right, items=right_labels, invert=True)

    return ((left_keep_labels, left_ignore_labels), (right_keep_labels, right_ignore_labels))


def flatten_multiindex(df: pd.DataFrame, axis: int = 0, delimiter: str = "_"):
    """
    Flatten (i.e. collapse) the multiindex on a particular ``axis`` using
    a ``delimiter``.

    Parameters
    ----------
    df : DataFrame
    axis : {0 or 'index', 1 or 'columns'}, default 0
        Whether to flatten labels from the index (0 or 'index') or
        columns (1 or 'columns').
    delimiter : str, default is "_"
        String to join multiindex levels on

    Examples
    --------
    Basic usage

    >>> df = pd.DataFrame({"PIDN": [1, 2], "InstrID": [3, 4]})
    >>> df.columns = pd.MultiIndex.from_product([["CDR"], df.columns])
    >>> df
       CDR
      PIDN InstrID
    0    1       3
    1    2       4

    >>> df.mac.flatten_multiindex(axis=1)
    >>> df
       CDR_PIDN  CDR_InstrID
    0         1            3
    1         2            4
    """

    axis_name = df._get_axis_name(axis)
    if axis_name == "index":
        if isinstance(df.index, pd.MultiIndex):
            df.index = [delimiter.join(str(idx) for idx in idx_tup) for idx_tup in df.index]
    elif axis_name == "columns":
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [delimiter.join(str(col) for col in col_tup) for col_tup in df.columns]


def get_col_name(df: pd.DataFrame, col_name):
    """
    Get the properly-cased column name from ``df``, ignoring case.

    Parameters
    ----------
    df : DataFrame
    col_name : str, tuple of str (for MultiIndexes)
        Case-insensitive name of the column.

    Returns
    -------
    str, tuple of str (if MultiIndex)
        The properly-cased column name.

    Raises
    ------
    KeyError
        If `col_name` is None or not found in the DataFrame.
    """

    if col_name is None:
        raise KeyError("column to get is 'None'")

    if lltools.is_list_like(col_name):
        # handle MultiIndex
        for col in df.columns:
            if lltools.list_like_str_equal(col, col_name, case_sensitive=False):
                return col
        raise KeyError(f"column not found: {col_name}")

    if isinstance(col_name, str):
        for col in df.columns:
            if strtools.str_equals(col, col_name, case_sensitive=False):
                return col

    raise KeyError(f"column not found: {col_name}")


def get_col_names(df: pd.DataFrame, col_names: List[str], strict=True):
    """
    Get the properly-cased columns names from ``df``, ignoring case.

    Parameters
    ----------
    df : DataFrame
    col_names : list-like
        List of case-insensitive column names
    strict : bool, default True
        If True, raise error if a column can't be found, otherwise
        return None for that column

    Returns
    -------
    list
        The list of properly-cased column names.
    """

    df_col_names = []
    for col in col_names:
        try:
            df_col = get_col_name(df, col)
        except KeyError as e:
            if strict:
                raise e
            else:
                df_col = None
        df_col_names.append(df_col)
    return df_col_names


def get_cols_by_prefixes(df: pd.DataFrame, prefixes, one_match_only=True):
    """
    Get columns that start with the prefixes.

    Parameters
    ----------
    df : DataFrame
    prefixes: str, or list of strs
        Column labels that start with the prefixes will be returned.
    one_match_only: bool, default True
        If True, raise error if a prefix matches more than one column.

    Returns
    -------
    dictionary
        A dict that maps each prefix to list of columns (Series)
        that start with that prefix.

    Raises
    ------
    KeyError
        If `one_match_only` is True, yet multiple columns found.

    Examples
    --------
    >>> df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    >>> df
        col1  col2
    0     1     3
    1     2     4
    >>> df.mac.get_cols_by_prefixes("col1")
    defaultdict(
        <class 'list'>,
        {
            'col1': [0    1
                     1    2
                     Name: col1, dtype: int64]
        }
    )

    >>> df.mac.get_cols_by_prefixes(["col1","col2"])
    defaultdict(
        <class 'list'>,
        {
            'col2': [0    3
                     1    4
                     Name: col2, dtype: int64],
            'col1': [0    1
                     1    2
                     Name: col1, dtype: int64]
        }
    )

    If you want to allow more than one match for prefixes,
    set `one_match_only`=`False`.

    >>> df.mac.get_cols_by_prefixes("col",one_match_only=False)
    defaultdict(
        <class 'list'>,
        {
            'col': [0    1
                    1    2
                    Name: col1, dtype: int64,
                    0    3
                    1    4
                    Name: col2, dtype: int64]
        }
    )
    """

    results = defaultdict(list)

    prefixes = set(lltools.maybe_make_list(prefixes))
    for prefix in prefixes:
        matched_cols = list(
            filter(lambda df_col: df_col.lower().startswith(prefix.lower()), df.columns)
        )

        if one_match_only and len(matched_cols) > 1:
            raise KeyError(f"Multiple columns start with prefix: {matched_cols}")

        for matched_col in matched_cols:
            results[prefix].append(df[matched_col])

    results.default_factory = None

    return results


def insert(df: pd.DataFrame, col_name, col_value, allow_duplicates=False):
    """
    Adds a column to the end of the DataFrame

    Parameters
    ----------
    df : DataFrame
    col_name : str
        Name of column to insert
    col_value : str
        Value of column to insert
    allow_duplicates : bool, default False
        Whether to allow a duplicate column name to be added
    """

    return df.insert(len(df.columns), col_name, col_value, allow_duplicates=allow_duplicates)


def is_date_col(arr_or_dtype):
    """
    Check whether the provided array or dtype is of the datetime64 dtype.

    Parameters
    ----------
    arr_or_dtype : array or dtype
    """

    return pd.api.types.is_datetime64_any_dtype(arr_or_dtype)


def mark_duplicates_by_cols(df: pd.DataFrame, cols: List[str]):
    """
    Create a column in ``df`` called ``_duplicates`` which is a boolean Series
    denoting duplicate rows as identified by ``cols``.

    Parameters
    ----------
    df : DataFrame
    cols : list-like
        Only consider these columns for identifiying duplicates
    """

    df[get_option("column.system.duplicates")] = df.duplicated(subset=cols, keep=False)
    return df


def replace_suffix(df: pd.DataFrame, old_suffix, new_suffix):
    """
    For any column names containing ``old_suffix``, replace the ``old_suffix``
    with ``new_suffix``.

    Parameters
    ----------
    df : DataFrame
    old_suffix : str
        suffix to replace
    new_suffix : str
        suffix to replace ``old_suffix``
    """

    return df.rename(
        columns=lambda x: x[: -len(old_suffix)] + new_suffix if x.endswith(old_suffix) else x
    )


def to_datetime(df: pd.DataFrame, date_col_name, **kwargs):
    """
    Convert ``date_col_name`` column in ``df`` to datetime.

    Parameters
    ----------
    df : DataFrame
    date_col_name : str
        Column to convert, case-insensitive
    **kwargs
        All keyword arguments are passed through to the underlying
        :func:`pandas.to_datetime` method.

    Returns
    -------
    str
        Properly-cased date column name.
    """

    try:
        _date_col = get_col_name(df, date_col_name)
        if not is_date_col(df[_date_col]):
            df[_date_col] = pd.to_datetime(df[_date_col], **kwargs)
        return _date_col
    except KeyError:
        raise KeyError(f"Date column '{date_col_name}' in dataframe is not a valid column")
    except Exception:
        raise
