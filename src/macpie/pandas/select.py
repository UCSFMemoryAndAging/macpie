from collections import defaultdict
import itertools
from typing import List

import pandas as pd

import macpie.pandas as mppd
from macpie.tools import lltools, strtools


def filter_by_id(df: pd.DataFrame, id_col_name: str, ids: List[int]) -> pd.DataFrame:
    """
    Filters a :class:`pandas.DataFrame` object to only include a specified list
    of numerical IDs in a specified numerical ID column.

    Parameters
    ----------
    df : DataFrame
        To be filtered
    id_col_name : str
        The DataFrame column to filter on
    ids: list
        The list of IDs to filter on in the ``id_col_name`` column

    Returns
    -------
    DataFrame
        A DataFrame of the filtered result.
    """

    try:
        _ids = [int(i) for i in ids]
    except ValueError as error:
        raise ValueError(f"ids list contains an invalid number: {error}")

    _id_col = df.mac.get_col_name(id_col_name)

    return df.loc[df[_id_col].isin(_ids)].reset_index(drop=True)


def filter_labels(
    *dfs: pd.DataFrame,
    axis=None,
    filter_level=None,
    result_level=None,
    result_type="single_list",
    **kwargs,
):
    """
    Filter dataframe row or column labels. The options ``items``, ``like``,
    and ``regex`` are additive and can be used in conjunction with one another.

    Parameters
    ----------
    dfs : Sequence of DataFrames
    axis : {0 or `index`, 1 or `columns`, None}, default None
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
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`macpie.lltools.filter_seq` function to perform the actual filtering.

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
            "Invalid value for result_type, must be one "
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

        _, filtered_idxs = lltools.filter_seq(labels, **kwargs)

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
            final_result = list(lltools.remove_duplicates(final_result))

    return final_result


def filter_labels_pair(left: pd.DataFrame, right: pd.DataFrame, axis=None, **kwargs):
    """
    Filter row or column labels on a pair of dataframes.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    axis : {0 or `index`, 1 or `columns`, None}, default None
        The axis to filter labels on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`macpie.lltools.filter_seq_pair` function to perform the actual
        label filtering.

    Returns
    -------
    Tuple[Tuple[str, str], Tuple[str, str]]
        ((left_labels_kept, right_labels_kept), (left_labels_discarded, right_labels_discarded))
    """
    if axis is None:
        axis = left._info_axis_name

    left_labels = left._get_axis(axis)
    right_labels = right._get_axis(axis)

    return lltools.filter_seq_pair(left_labels, right_labels, **kwargs)


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

    count = mppd.count_trailers(
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

    Examples
    --------
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


def subset(*dfs: pd.DataFrame, **kwargs):
    """
    Subset rows or columns of one or more DataFrames according to filtered labels.

    Parameters
    ----------
    dfs : Sequence of DataFrames
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`macpie.pandas.filter_labels` function for filtering.

    Returns
    -------
    DataFrame
        Subsetted DataFrame
    """
    axis = kwargs.pop("axis", dfs[0]._info_axis_name)
    kwargs.pop("result_level", None)
    kwargs.pop("result_type", None)

    for df in dfs:
        subsetted_labels = filter_labels(df, axis=axis, result_level=None, **kwargs)
        subsetted_df = df.drop(labels=subsetted_labels, axis=axis)
        yield subsetted_df


def subset_pair(
    left: pd.DataFrame,
    right: pd.DataFrame,
    axis=None,
    **kwargs,
):
    """
    Subset rows or columns of a pair of dataframes according to filtered labels.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    axis : {0 or `index`, 1 or `columns`, None}, default None
        The axis to filter labels on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`macpie.pandas.filter_labels_pair` function for filtering.

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
        axis=axis,
        **kwargs,
    )

    left = left.drop(labels=left_labels_to_drop, axis=axis)
    right = right.drop(labels=right_labels_to_drop, axis=axis)

    return (left, right)
