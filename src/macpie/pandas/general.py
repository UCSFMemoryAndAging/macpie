from dateutil.parser import ParserError
from typing import List

import numpy as np
import pandas as pd

from macpie.util import is_list_like, list_like_str_equal, strip_suffix

COL_KEYWORDS = {'_abs_diff_days', '_diff_days', '_duplicates', '_merge'}


def add_diff_days(df: pd.DataFrame, col_start: str, col_end: str):
    if col_start == col_end:
        raise KeyError("date columns have the same name: {col_start}")
    df['_diff_days'] = df[col_end] - df[col_start]
    df['_diff_days'] = df['_diff_days'] / np.timedelta64(1, 'D')
    return df


def any_duplicates(df: pd.DataFrame, col: str, ignore_nan: bool = False):
    col = get_col_name(df, col)
    if ignore_nan is True:
        return df[col].dropna().duplicated().any()
    return df[col].duplicated().any()


def assimilate(a: pd.DataFrame, b: pd.DataFrame):
    # assimilate b to look like a
    # give me all the elments in a that are also in b

    # if one set of columns are MultiIndex, then both should be
    if isinstance(a.columns, pd.MultiIndex) or isinstance(b.columns, pd.MultiIndex):
        if not isinstance(a.columns, pd.MultiIndex) or not isinstance(b.columns, pd.MultiIndex):
            raise IndexError('One set of columns is a MultiIndex and the other is not.')

    a_columns = set(a.columns)
    b_columns = set(b.columns)

    # find columns that are only in a but not in b
    diff_cols = a_columns.difference(b_columns)

    a_dtypes = a.dtypes.to_dict()

    for col_name in diff_cols:
        a_dtypes.pop(col_name)

    return b.astype(a_dtypes)


def diff_cols(a: pd.DataFrame, b: pd.DataFrame, cols_ignore=None):
    a_columns = set(a.columns)
    a_columns = a_columns.difference(COL_KEYWORDS)

    b_columns = set(b.columns)
    b_columns = b_columns.difference(COL_KEYWORDS)

    if cols_ignore is not None and len(cols_ignore) > 0:
        for col in cols_ignore:
            a_columns.discard(col)
            b_columns.discard(col)

    left_only_cols = a_columns.difference(b_columns)
    right_only_cols = b_columns.difference(a_columns)

    return (left_only_cols, right_only_cols)


def diff_rows(a: pd.DataFrame, b: pd.DataFrame, cols_ignore=None):
    # if one set of columns are MultiIndex, then both should be
    if isinstance(a.columns, pd.MultiIndex) or isinstance(b.columns, pd.MultiIndex):
        if not isinstance(a.columns, pd.MultiIndex) or not isinstance(b.columns, pd.MultiIndex):
            raise IndexError('One set of columns is a MultiIndex and the other is not.')

    if isinstance(a.columns, pd.MultiIndex):
        level = len(a.columns.levels) - 1
        _a = a.drop(columns=COL_KEYWORDS, level=level, errors='ignore')
        _b = b.drop(columns=COL_KEYWORDS, level=level, errors='ignore')
        _a.columns = _a.columns.to_flat_index()
        _b.columns = _b.columns.to_flat_index()
    else:
        _a = a.drop(columns=COL_KEYWORDS, errors='ignore')
        _b = b.drop(columns=COL_KEYWORDS, errors='ignore')

    if cols_ignore is not None and len(cols_ignore) > 0:
        _a.drop(columns=cols_ignore, inplace=True, errors='ignore')
        _b.drop(columns=cols_ignore, inplace=True, errors='ignore')

    a_columns = _a.columns
    b_columns = _b.columns

    if set(a_columns) == set(b_columns):
        merged_df = pd.merge(_a, _b, indicator=True, how='outer')
        changed_rows_df = merged_df[merged_df['_merge'] != 'both']
        return changed_rows_df

    raise KeyError('Dataframes do not share the same columns')


def drop_suffix(df: pd.DataFrame, suffix):
    return df.rename(columns=lambda x: strip_suffix(x, suffix))


def flatten_multiindex(df: pd.DataFrame, axis: int = 0, delimiter: str = '_'):
    if axis == 0:
        if isinstance(df.index, pd.MultiIndex):
            df.index = [delimiter.join(str(idx) for idx in idx_tup) for idx_tup in df.index]
    elif axis == 1:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [delimiter.join(str(col) for col in col_tup) for col_tup in df.columns]


def get_col_name(df: pd.DataFrame, col_name):
    if col_name is None:
        raise KeyError("column to get is 'None'")

    if is_list_like(col_name):
        for col in df.columns:
            if list_like_str_equal(col, col_name, True):
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
    for index, col_name in enumerate(col_names):
        col_names[index] = get_col_name(df, col_name)
    return col_names


def is_date_col(arr_or_dtype):
    return pd.api.types.is_datetime64_any_dtype(arr_or_dtype)


def mark_duplicates_by_cols(df: pd.DataFrame, cols: List[str]):
    df['_duplicates'] = df.duplicated(subset=cols, keep=False)
    return df


def num_cols(df: pd.DataFrame):
    # faster than df.shape[1]
    return len(df.columns)


def num_rows(df: pd.DataFrame):
    # faster than df.shape[0] or len(df)
    return len(df.index)


def replace_suffix(df: pd.DataFrame, old_suffix, new_suffix):
    return df.rename(columns=lambda x: x[:-len(old_suffix)] + new_suffix if x.endswith(old_suffix) else x)


def to_datetime(df: pd.DataFrame, date_col: str):
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
