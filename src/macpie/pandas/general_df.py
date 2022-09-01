import itertools
from collections import defaultdict
from typing import List

import numpy as np
import pandas as pd

import macpie as mp


def add_diff_days(
    df: pd.DataFrame, col_start: str, col_end: str, diff_days_col: str = None, inplace=False
):
    """
    Adds a column whos values are the number of days between ``col_start`` and ``col_end``

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
        diff_days_col = mp.get_option("column.system.diff_days")

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

    col = get_col_name(df, col)
    if ignore_nan is True:
        return df[col].dropna().duplicated().any()
    return df[col].duplicated().any()


def assimilate(left: pd.DataFrame, right: pd.DataFrame):
    """
    Assimilate ``right`` to look like ``left`` by ordering the columns in ``right``
    as close to the order of the columns in ``left``, and by casting column data types
    in ``right`` to the column data types in ``left`` where the column name is the same.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame

    Returns
    -------
    DataFrame
        The assimilated ``right`` DataFrame
    """

    # 1. Order the right columns as close to the order of the left columns
    ((left_labels_returned, _), (_, right_labels_discarded)) = filter_labels_pair(
        left, right, intersection=True
    )
    common_columns = left_labels_returned
    right_columns_reordered = common_columns + right_labels_discarded
    right = right.reindex(right_columns_reordered, axis="columns")

    # 2. Cast column data types in right to be the same as those in left
    for col in common_columns:
        right[col] = right[col].astype(left[col].dtypes.name)

    return right


def compare(left: pd.DataFrame, right: pd.DataFrame, filter_kwargs={}, **kwargs):
    """
    Compare to another DataFrame and show the differences.

    Parameters
    ----------
    left : DataFrame
        DataFrame to compare.
    right : DataFrame
        DataFrame to compare with.
    filter_kwargs : dict, optional
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_pair`
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
        (left, right) = filter_pair(left, right, **filter_kwargs)

    try:
        return left.compare(right, **kwargs)
    except ValueError:  # if dfs don't have identical labels or shape
        # first compare columns
        (left_only_cols, right_only_cols) = left.mac.diff_cols(right)
        if left_only_cols or right_only_cols:
            col_diffs = pd.DataFrame()
            col_diffs["Left_Only_Cols"] = left_only_cols
            col_diffs["Right_Only_Cols"] = right_only_cols
            return col_diffs
        else:
            # then compare rows
            return left.mac.diff_rows(right)


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
        ((left_cols, right_cols), _) = filter_labels_pair(left, right, **filter_kwargs)
    else:
        left_cols = left.columns
        right_cols = right.columns

    left_cols = list(mp.lltools.remove_duplicates(left_cols))
    right_cols = list(mp.lltools.remove_duplicates(right_cols))

    left_only_cols = mp.lltools.difference(left_cols, right_cols)
    right_only_cols = mp.lltools.difference(right_cols, left_cols)

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
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_pair`
        to pre-filter columns before comparison.

    Returns
    -------
    DataFrame
    """
    if filter_kwargs:
        (left, right) = filter_pair(left, right, **filter_kwargs)

    left_cols = left.columns
    right_cols = right.columns

    if set(left_cols) == set(right_cols):
        indicator_col_name = mp.get_option("column.system.prefix") + "_diff_rows_merge"
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

    return df.rename(columns=lambda x: mp.strtools.strip_suffix(x, suffix))


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
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_pair`
        to pre-filter columns before comparison.

    Returns
    -------
    bool
        True if all elements, except those in filtered out columns,
        are the same in both objects, False otherwise.
    """
    if filter_kwargs:
        (left, right) = filter_pair(left, right, **filter_kwargs)
    return left.equals(right)


def filter_labels(
    *dfs: pd.DataFrame,
    items=None,
    like=None,
    regex=None,
    invert=False,
    axis=None,
    filter_level=None,
    result_level=None,
    result_type="single_list",
):
    """
    Filter dataframe row or column labels. The options ``items``, ``like``,
    and ``regex`` are additive and can be used in conjunction with one another.

    Parameters
    ----------
    items : list-like
        Get labels from axis which are in `items`.
    like : str
        Get labels from axis for which "like in label == True".
    regex : str (regular expression)
        Get labels from axis for which re.search(regex, label) == True.
    invert : bool, default False
        Whether to invert the result (i.e. discard labels returned by
        `items`, `like`, or `regex`)
    axis : {0 or ‘index’, 1 or ‘columns’, None}, default None
        The axis to filter labels on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.
    filter_level : str or int, optional
        For a MultiIndex, level (name or number) to use for
        filtering. Supports negative indexing (i.e. -1 is highest level).
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
    """

    if result_type not in ["single_list", "single_list_no_dups", "list_of_lists"]:
        raise ValueError(
            "invalid value for result_type, must be one "
            "of {'single_list', 'single_list_no_dups', 'list_of_lists'}"
        )

    if axis is None:
        axis = dfs[0]._info_axis_name

    final_result = []
    for df in dfs:
        labels = df._get_axis(axis)

        mi_labels = None
        if isinstance(labels, pd.MultiIndex):
            mi_labels = labels.copy()
            if filter_level is not None:
                if filter_level < 0:
                    # mimics negative indexing (i.e. -1 is the highest level)
                    mi_level = labels.nlevels + filter_level
                else:
                    mi_level = filter_level
                labels = mi_labels.get_level_values(mi_level)

        _, filtered_idxs = mp.lltools.filter_seq(
            labels, items=items, like=like, regex=regex, invert=invert
        )

        if mi_labels is not None:
            result = [mi_labels[idx] for idx in filtered_idxs]
            if result_level is not None:
                result_level = mi_labels._get_level_number(result_level)
                result = list(list(zip(*result))[result_level])
        else:
            result = [labels[idx] for idx in filtered_idxs]

        final_result.append(result)

    if result_type == "single_list" or result_type == "single_list_no_dups":
        final_result = list(itertools.chain.from_iterable(final_result))
        if result_type == "single_list_no_dups":
            final_result = list(mp.lltools.remove_duplicates(final_result))

    return final_result


def filter_labels_pair(
    left: pd.DataFrame,
    right: pd.DataFrame,
    filter_kwargs={},
    left_filter_kwargs={},
    right_filter_kwargs={},
    intersection=False,
    axis=None,
):
    """
    Filter row or column labels on a pair of dataframes.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    filter_kwargs : dict
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels`
        to be applied to both DataFrames.
    left_filter_kwargs : dict
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels`
        to be applied to left DataFrame.
    right_filter_kwargs : dict
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels`
        to be applied to right DataFrame.
    intersection : bool, default False
        Whether to only return the labels common to both, after excluding
        any labels filtered out by the *filter_kwargs params.
    axis : {0 or ‘index’, 1 or ‘columns’, None}, default None
        The axis to filter labels on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.

    Returns
    -------
    Tuple[Tuple[str, str], Tuple[str, str]]
        ((left_labels_kept, right_labels_kept), (left_labels_discarded, right_labels_discarded))
    """

    if axis is None:
        axis = left._info_axis_name

    left_labels = left._get_axis(axis)
    right_labels = right._get_axis(axis)

    return mp.lltools.filter_seq_pair(
        left_labels,
        right_labels,
        filter_kwargs=filter_kwargs,
        left_filter_kwargs=left_filter_kwargs,
        right_filter_kwargs=right_filter_kwargs,
        intersection=intersection,
    )


def filter_pair(
    left: pd.DataFrame,
    right: pd.DataFrame,
    filter_kwargs={},
    left_filter_kwargs={},
    right_filter_kwargs={},
    intersection=None,
    axis=None,
):
    """
    Subset rows or columns of a pair of dataframes according to filtered labels.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    filter_kwargs : list-like
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels_pair`
        to be applied to both DataFrames.
    left_filter_kwargs : dict
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels_pair`
        to be applied to left DataFrame.
    right_filter_kwargs : list-like
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_labels_pair`
        to be applied to right DataFrame.
    intersection : bool, default False
        Whether to only return the labels common to both, after excluding
        any labels filtered out by the *filter_kwargs params.
    axis : {0 or ‘index’, 1 or ‘columns’, None}, default None
        The axis to filter labels on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.

    Returns
    -------
    Tuple[DataFrame, DataFrame]
        (subsetted left dataframe, subsetted right dataframe)
    """
    if axis is None:
        axis = left._info_axis_name

    (_, (left_labels_to_drop, right_labels_to_drop)) = filter_labels_pair(
        left,
        right,
        filter_kwargs=filter_kwargs,
        left_filter_kwargs=left_filter_kwargs,
        right_filter_kwargs=right_filter_kwargs,
        intersection=intersection,
        axis=axis,
    )

    left = left.drop(labels=left_labels_to_drop, axis=axis)
    right = right.drop(labels=right_labels_to_drop, axis=axis)

    return (left, right)


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

    if mp.lltools.is_list_like(col_name):
        # handle MultiIndex
        for col in df.columns:
            if mp.lltools.list_like_str_equal(col, col_name, case_sensitive=False):
                return col
        raise KeyError(f"column not found: {col_name}")

    if isinstance(col_name, str):
        for col in df.columns:
            if mp.strtools.str_equals(col, col_name, case_sensitive=False):
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

    prefixes = set(mp.lltools.maybe_make_list(prefixes))
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


def insert(df: pd.DataFrame, col_name, col_value, **kwargs):
    """
    Adds a column to the end of the DataFrame

    Parameters
    ----------
    df : DataFrame
    col_name : str
        Name of column to insert
    col_value : str
        Value of column to insert
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :meth:`pandas.DataFrame.insert` method.
    """
    return df.insert(len(df.columns), col_name, col_value, **kwargs)


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
    Create a column in ``df`` called ``get_option("column.system.duplicates")``
    which is a boolean Series denoting duplicate rows as identified by ``cols``.

    Parameters
    ----------
    df : DataFrame
    cols : list-like
        Only consider these columns for identifiying duplicates
    """
    df[mp.get_option("column.system.duplicates")] = df.duplicated(subset=cols, keep=False)
    return df


def imitate_sort(left: pd.DataFrame, right: pd.DataFrame, left_kwargs={}, right_kwargs={}):
    """
    Sort the pair of DataFrames using their common columns.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    **kwargs
        All keyword arguments are passed through to the underlying
        :meth:`pandas.DataFrame.sort_values` method.
    """
    ((common_columns, _), _) = filter_labels_pair(left, right, intersection=True)
    left = left.sort_values(by=common_columns, **left_kwargs)
    right = right.sort_values(by=common_columns, **right_kwargs)

    return (left, right)


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
