from typing import List

import pandas as pd

from . import general
from . import operators


@pd.api.extensions.register_dataframe_accessor("mac")
class MacDataFrameAccessor:
    def __init__(self, df):
        self._validate(df)
        self._df = df

    @staticmethod
    def _validate(obj):
        pass

    # general functions
    def add_diff_days(self, col_start: str, col_end: str):
        return general.add_diff_days(self._df, col_start, col_end)

    def any_duplicates(self, col: str, ignore_nan: bool = False):
        return general.any_duplicates(self._df, col, ignore_nan)

    def assimilate(self, right: pd.DataFrame):
        return general.assimilate(self._df, right)

    def diff_cols(self, right: pd.DataFrame, cols_ignore=None):
        return general.diff_cols(self._df, right, cols_ignore)

    def diff_rows(self, right: pd.DataFrame, cols_ignore=None):
        return general.diff_rows(self._df, right, cols_ignore)

    def drop_suffix(self, suffix: str):
        return general.drop_suffix(self._df, suffix)

    def flatten_multiindex(self, axis: int = 0, delimiter: str = '_'):
        return general.flatten_multiindex(self._df, axis)

    def get_col_name(self, col_name: str):
        return general.get_col_name(self._df, col_name)

    def get_col_names(self, col_names: List[str]):
        return general.get_col_names(self._df, col_names)

    def is_date_col(self, arr_or_dtype):
        return general.is_date_col(self._df[arr_or_dtype])

    def json_dumps_contents(self):
        return general.json_dumps_contents(self._df)

    def json_loads_contents(self):
        return general.json_loads_contents(self._df)

    def mark_duplicates_by_cols(self, cols: List[str]):
        return general.mark_duplicates_by_cols(self._df, cols)

    def num_rows(self):
        return general.num_rows(self._df)

    def num_cols(self):
        return general.num_cols(self._df)

    def replace_suffix(self, old_suffix, new_suffix):
        return general.replace_suffix(self._df, old_suffix, new_suffix)

    def to_datetime(self, date_col):
        return general.to_datetime(self._df, date_col)

    # operators
    def date_proximity(
        self,
        right: pd.DataFrame,
        id_on=None,
        id_left_on=None,
        id_right_on=None,
        date_on=None,
        date_left_on=None,
        date_right_on=None,
        get: str = 'all',
        when: str = 'earlier_or_later',
        days: int = 90,
        left_link_id=None,
        dropna: bool = False,
        merge='partial',
        merge_suffixes=('_x', '_y')
    ):
        return operators.date_proximity.date_proximity(
            self._df,
            right,
            id_on=id_on,
            id_left_on=id_left_on,
            id_right_on=id_right_on,
            date_on=date_on,
            date_left_on=date_left_on,
            date_right_on=date_right_on,
            get=get,
            when=when,
            days=days,
            left_link_id=left_link_id,
            dropna=dropna,
            merge=merge,
            merge_suffixes=merge_suffixes
        )

    def filter_by_id(
        self,
        id_col: str,
        ids: List[int]
    ):
        return operators.filter_by_id.filter_by_id(
            self._df,
            id_col,
            ids
        )

    def group_by_keep_one(
        self,
        group_by_col: str,
        date_col: str,
        keep: str = 'all',
        id_col: str = None,
        drop_duplicates: bool = False
    ):
        return operators.group_by_keep_one.group_by_keep_one(
            self._df,
            group_by_col=group_by_col,
            date_col=date_col,
            keep=keep,
            id_col=id_col,
            drop_duplicates=drop_duplicates
        )

    def merge(
        self,
        right: pd.DataFrame,
        on=None,
        left_on=None,
        right_on=None,
        merge_suffixes=('_x', '_y'),
        add_suffixes=False,
        add_indexes=(None, None)
    ):
        return operators.merge.merge(
            self._df,
            right,
            on=on,
            left_on=left_on,
            right_on=right_on,
            merge_suffixes=merge_suffixes,
            add_suffixes=add_suffixes,
            add_indexes=add_indexes
        )
