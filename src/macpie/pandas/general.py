from collections import defaultdict
import dateutil
from typing import List

import numpy as np
import pandas as pd

from macpie._config import get_option
from macpie import itertools, lltools, strtools


def add_diff_days(
    df: pd.DataFrame, col_start: str, col_end: str, diff_days_col: str = None, inplace=False
):
    """Adds a column to DataFrame called ``_diff_days`` which contains
    the number of days between ``col_start`` and ``col_end``

    :param df: DataFrame
    :param col_start: column containing the start date
    :param col_end: column containing the end date
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
    """Return ``True`` if there are any duplicates in ``col``.

    :param df: DataFrame
    :param col: column to check for duplicates
    :param ignore_nan: Whether to ignore ``nan`` values
    """
    col = get_col_name(df, col)
    if ignore_nan is True:
        return df[col].dropna().duplicated().any()
    return df[col].duplicated().any()


def assimilate(left: pd.DataFrame, right: pd.DataFrame):
    """Assimilate ``right`` to look like ``left`` by casting column data types in ``right``
    to the data types in ``left`` where the column name is the same.

    :param left: left DataFrame
    :param right: right DataFrame
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


def diff_cols(left: pd.DataFrame, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat=None):
    """Return a length-2 tuple where the first element is the set of columns that
    exist in ``left``, and the second element is the set of columns that only
    exist in ``right``.

    :param left: left DataFrame
    :param right: right DataFrame
    :param cols_ignore: columns to ignore
    :param cols_ignore_pat: Character sequence or regular expression.
                            Column names that match will be ignored.
                            Defaults to None, which uses the pattern
                            ``'$^'`` to match nothing to ignore nothing
    """
    left = drop_cols(left, cols_list=cols_ignore, cols_pat=cols_ignore_pat)
    right = drop_cols(right, cols_list=cols_ignore, cols_pat=cols_ignore_pat)

    left_columns = set(left.columns)
    right_columns = set(right.columns)

    left_columns = left_columns - set(cols_ignore)
    right_columns = right_columns - set(cols_ignore)

    left_only_cols = left_columns - right_columns
    right_only_cols = right_columns - left_columns

    return (left_only_cols, right_only_cols)


def diff_rows(left: pd.DataFrame, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat=None):
    """If ``left`` and ``right`` share the same columns, returns a DataFrame
    containing rows that differ.

    :param left: left DataFrame
    :param right: right DataFrame
    :param cols_ignore: a list of any columns to ignore
    """
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


def drop_cols(df: pd.DataFrame, cols_list=set(), cols_pat=None):
    """Drop specified columns

    :param cols_list: List of columns to drop. Defaults to set()
    :param cols_pat: Character sequence or regular expression.
                     Column names that match will be dropped.
                     Defaults to None, which uses the pattern
                     ``'$^'`` to match nothing to ignore nothing
    """
    # Default pattern is to match nothing to ignore nothing
    cols_pat = "$^" if cols_pat is None else cols_pat

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
    """Removes the ``suffix`` in any column name containing the ``suffix``.

    :param df: DataFrame
    :param suffix: suffix to drop
    """
    return df.rename(columns=lambda x: strtools.strip_suffix(x, suffix))


def equals(left: pd.DataFrame, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat=None):
    """For testing equality of :class:`pandas.DataFrame` objects

    :param df1: left DataFrame to compare
    :param df2: right DataFrame to compare
    :param cols_ignore: DataFrame columns to ignore in comparison
    :param cols_ignore_pat: Character sequence or regular expression.
                            Column names that match will be ignored in comparison.
                            Defaults to None, which uses the pattern
                            ``'$^'`` to match nothing to ignore nothing
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


def flatten_multiindex(df: pd.DataFrame, axis: int = 0, delimiter: str = "_"):
    """
    Flatten (i.e. collapse) the multiindex on a particular ``axis`` using
    a ``delimiter``.

    Parameters
    ----------
    df : DataFrame.
    axis : {0 or 'index', 1 or 'columns'}, default 0
        Whether to flatten labels from the index (0 or 'index') or
        columns (1 or 'columns').
    delimiter : str
        string to join multiindex levels on

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
    """Get the properly-cased column name from ``df``, ignoring case.

    :param df: DataFrame
    :param col_name: case-insensitive name of the column
    """

    if col_name is None:
        raise KeyError("column to get is 'None'")

    if lltools.is_list_like(col_name):
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
    """Get the properly-cased columns names from ``df``, ignoring case.

    :param df: DataFrame
    :param col_names: list of case-insensitive column names
    :param strict: if True, raise error if a column can't be found, otherwise
                   return None for that column
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
    """Get columns that start with the prefixes.

    Parameters
    ----------
    df : DataFrame
    prefixes: str, or list of strs
        Column labels that start with the prefixes will be returned.
    one_match_only: bool, optional
        If True, raise error if a prefix matches more than one column.

    Returns
    -------
    dictionary
        A dict that maps each prefix to list of columns (Series)
        that start with that prefix.

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
    """Adds a column to the end of the DataFrame

    :param df: DataFrame
    :param col_name: name of column to insert
    :param col_value: value of column to insert
    """
    return df.insert(len(df.columns), col_name, col_value, allow_duplicates=allow_duplicates)


def is_date_col(arr_or_dtype):
    """Check whether the provided array or dtype is of the datetime64 dtype.

    :param arr_or_dtype: The array or dtype to check
    """
    return pd.api.types.is_datetime64_any_dtype(arr_or_dtype)


def mark_duplicates_by_cols(df: pd.DataFrame, cols: List[str]):
    """Create a column in ``df`` called ``_duplicates`` which is a boolean Series
    denoting duplicate rows as identified by ``cols``.

    :param df: DataFrame
    :param cols: Only consider these columns for identifiying duplicates
    """
    df[get_option("column.system.duplicates")] = df.duplicated(subset=cols, keep=False)
    return df


def replace_suffix(df: pd.DataFrame, old_suffix, new_suffix):
    """For any column names containing ``old_suffix``, replace the ``old_suffix``
    with ``new_suffix``.

    :param df: DataFrame
    :param old_suffix: suffix to replace
    :param new_suffix: suffix to replace ``old_suffix``
    """
    return df.rename(
        columns=lambda x: x[: -len(old_suffix)] + new_suffix if x.endswith(old_suffix) else x
    )


def to_datetime(df: pd.DataFrame, date_col_name, **kwargs):
    """Convert ``date_col_name`` column in ``df`` to datetime.

    :param df: DataFrame
    :param date_col_name: column to convert
    """
    try:
        _date_col = get_col_name(df, date_col_name)
        if not is_date_col(df[_date_col], **kwargs):
            df[_date_col] = pd.to_datetime(df[_date_col])
        return _date_col
    except KeyError:
        raise KeyError(f"Date column '{date_col_name}' in dataframe is not a valid column")
    except Exception:
        raise
