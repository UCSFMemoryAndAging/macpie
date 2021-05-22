from dateutil.parser import ParserError
import json
from typing import List

import numpy as np
import pandas as pd

from macpie._config import get_option
from macpie.io.json import MACPieJSONDecoder, MACPieJSONEncoder
from macpie.tools import sequence as seqtools
from macpie.tools import string as strtools


def add_diff_days(df: pd.DataFrame, col_start: str, col_end: str):
    """Adds a column to DataFrame called ``_diff_days`` which contains
    the number of days between ``col_start`` and ``col_end``

    :param df: DataFrame
    :param col_start: column containing the start date
    :param col_end: column containing the end date
    """
    diff_days_col = get_option("column.system.diff_days")
    if col_start == col_end:
        raise KeyError("date columns have the same name: {col_start}")
    df[diff_days_col] = df[col_end] - df[col_start]
    df[diff_days_col] = df[diff_days_col] / np.timedelta64(1, 'D')
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

    # if one set of columns are MultiIndex, then both should be
    if isinstance(left.columns, pd.MultiIndex) or isinstance(right.columns, pd.MultiIndex):
        if not isinstance(left.columns, pd.MultiIndex) or not isinstance(right.columns, pd.MultiIndex):
            raise IndexError('One set of columns is a MultiIndex and the other is not.')

    left_columns = set(left.columns)
    right_columns = set(right.columns)

    # find columns that are only in left but not in right
    diff_cols = left_columns.difference(right_columns)

    left_dtypes = left.dtypes.to_dict()

    for col_name in diff_cols:
        left_dtypes.pop(col_name)

    return right.astype(left_dtypes)


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
        indicator_col_name = get_option("column.system.prefix") + '_diff_rows_merge'
        if isinstance(left.columns, pd.MultiIndex) or isinstance(right.columns, pd.MultiIndex):
            # TODO: Doing a pd.merge() on MultiIndex dataframes with indicator
            # set to True/string resulted in the following error:
            # pandas.errors.PerformanceWarning: dropping on a non-lexsorted multi-index
            # without a level parameter may impact performance
            # Flatten the column MultiIndexes to get around this
            left.columns = left.columns.to_flat_index()
            right.columns = right.columns.to_flat_index()
        merged_df = pd.merge(left, right, indicator=indicator_col_name, how='outer')
        changed_rows_df = merged_df[merged_df[indicator_col_name] != 'both']
        return changed_rows_df

    raise KeyError('Dataframes do not share the same columns')


def drop_cols(df: pd.DataFrame, cols_list=set(), cols_pat=None):
    """Drop specified columns

    :param cols_list: List of columns to drop. Defaults to set()
    :param cols_pat: Character sequence or regular expression.
                     Column names that match will be dropped.
                     Defaults to None, which uses the pattern
                     ``'$^'`` to match nothing to ignore nothing
    """
    # Default pattern is to match nothing to ignore nothing
    cols_pat = '$^' if cols_pat is None else cols_pat

    if isinstance(df.columns, pd.MultiIndex):
        last_level = df.columns.nlevels - 1
        cols_match_pat = df.columns.get_level_values(last_level).str.contains(cols_pat, regex=True)
    else:
        cols_match_pat = df.columns.str.contains(cols_pat, regex=True)

    cols_to_keep = np.invert(cols_match_pat)

    df = df.loc[:, cols_to_keep]

    df = df.drop(columns=cols_list, errors='ignore')

    return df


def drop_suffix(df: pd.DataFrame, suffix):
    """Removes the ``suffix`` in any column name containing the ``suffix``.

    :param df: DataFrame
    :param suffix: suffix to drop
    """
    return df.rename(columns=lambda x: strtools.strip_suffix(x, suffix))


def equals(
    left: pd.DataFrame,
    right: pd.DataFrame,
    cols_ignore=set(),
    cols_ignore_pat=None
):
    """For testing equality of :class:`pandas.DataFrame` objects

    :param df1: left DataFrame to compare
    :param df2: right DataFrame to compare
    :param cols_ignore: DataFrame columns to ignore in comparison
    :param cols_ignore_pat: Character sequence or regular expression.
                            Column names that match will be ignored in comparison.
                            Defaults to None, which uses the pattern
                            ``'$^'`` to match nothing to ignore nothing
    """
    if isinstance(left.columns, pd.MultiIndex) or isinstance(right.columns, pd.MultiIndex):
        if not isinstance(left.columns, pd.MultiIndex) or not isinstance(right.columns, pd.MultiIndex):
            raise IndexError('One set of columns is a MultiIndex and the other is not.')
        if left.columns.nlevels != right.columns.nlevels:
            raise IndexError('MultiIndexes have different levels.')

    left = drop_cols(left, cols_list=cols_ignore, cols_pat=cols_ignore_pat)
    right = drop_cols(right, cols_list=cols_ignore, cols_pat=cols_ignore_pat)

    right = left.mac.assimilate(right)

    return left.equals(right)


def flatten_multiindex(df: pd.DataFrame, axis: int = 0, delimiter: str = '_'):
    """Flatten (i.e. collapse) the multiindex on a particular ``axis`` using
    a ``delimiter``.

    :param df: DataFrame
    :param axis: on which axis to flatten the multiindex. ``0`` for index, ``1`` for columns
    :param delimiter: delimiter to join multiindex levels on
    """
    if axis == 0:
        if isinstance(df.index, pd.MultiIndex):
            df.index = [delimiter.join(str(idx) for idx in idx_tup) for idx_tup in df.index]
    elif axis == 1:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [delimiter.join(str(col) for col in col_tup) for col_tup in df.columns]


def get_col_name(df: pd.DataFrame, col_name):
    """Get the properly-cased column name from ``df``, ignoring case.

    :param df: DataFrame
    :param col_name: case-insensitive name of the column
    """
    if col_name is None:
        raise KeyError("column to get is 'None'")

    if seqtools.is_list_like(col_name):
        for col in df.columns:
            if seqtools.list_like_str_equal(col, col_name, True):
                return col
        raise KeyError(f"column not found: {col_name}")

    if isinstance(col_name, str):
        for col in df.columns:
            if isinstance(col, str) and col.lower() == col_name.lower():
                return col
    else:
        for col in df.columns:
            if col == col_name:
                return col

    raise KeyError(f"column not found: {col_name}")


def get_col_names(df: pd.DataFrame, col_names: List[str]):
    """Get the properly-cased columns names from ``df``, ignoring case.

    :param df: DataFrame
    :param col_names: list of case-insensitive column names
    """
    for index, col_name in enumerate(col_names):
        col_names[index] = get_col_name(df, col_name)
    return col_names


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


def json_dumps_contents(df: pd.DataFrame):
    """Perform a json.dumps of each value in ``df``.

    :param df: DataFrame
    """
    return df.applymap(lambda a: json.dumps(a, cls=MACPieJSONEncoder))


def json_loads_contents(df: pd.DataFrame):
    """Perform a json.loads of each value in ``df``.

    :param df: DataFrame
    """
    return df.applymap(lambda a: json.loads(a, cls=MACPieJSONDecoder) if isinstance(a, str) else a)


def mark_duplicates_by_cols(df: pd.DataFrame, cols: List[str]):
    """Create a column in ``df`` called ``_duplicates`` which is a boolean Series
    denoting duplicate rows as identified by ``cols``.

    :param df: DataFrame
    :param cols: Only consider these columns for identifiying duplicates
    """
    df[get_option("column.system.duplicates")] = df.duplicated(subset=cols, keep=False)
    return df


def num_cols(df: pd.DataFrame):
    """Return number of columns in ``df``.

    :param df: DataFrame
    """
    # faster than df.shape[1]
    return len(df.columns)


def num_rows(df: pd.DataFrame):
    """Return number of rows in ``df``.

    :param df: DataFrame
    """
    # faster than df.shape[0] or len(df)
    return len(df.index)


def replace_suffix(df: pd.DataFrame, old_suffix, new_suffix):
    """For any column names containing ``old_suffix``, replace the ``old_suffix``
    with ``new_suffix``.

    :param df: DataFrame
    :param old_suffix: suffix to replace
    :param new_suffix: suffix to replace ``old_suffix``
    """
    return df.rename(columns=lambda x: x[:-len(old_suffix)] + new_suffix if x.endswith(old_suffix) else x)


def to_datetime(df: pd.DataFrame, date_col: str):
    """Convert ``date_col`` column in ``df`` to datetime.

    :param df: DataFrame
    :param date_col: column to convert
    """
    try:
        _date_col = get_col_name(df, date_col)
        if not is_date_col(df[_date_col]):
            df[_date_col] = pd.to_datetime(df[_date_col])
        return _date_col
    except KeyError:
        raise KeyError(f"Date column '{date_col}' in dataframe is not a valid column")
    except ValueError:
        raise ValueError(f"Date column '{date_col}' in dataframe contains string(s) that "
                         "are not likely datetime(s)")
    except TypeError as e:
        raise TypeError((f"Date column '{date_col}' in dataframe contains values "
                        f"that are not convertible to datetime")) from e
    except ParserError:
        raise ValueError((f"Date column '{date_col}' in dataframe could not be parsed "
                         f"as a datetime string"))
    except pd.errors.OutOfBoundsDatetime:
        # Since pandas represents timestamps in nanosecond resolution,
        # the time span that can be represented using a 64-bit integer
        # is limited to approximately 584 years.
        raise ValueError((f"Date column '{date_col}' in dataframe contains a date "
                         f"that is out of bounds (i.e. outside of today +- 584 years)"))
