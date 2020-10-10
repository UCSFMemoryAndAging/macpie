import pandas as pd

from .general import *
from .operators.date_proximity import date_proximity
from .operators.filter_by_id import filter_by_id
from .operators.group_by_keep_one import group_by_keep_one


@pd.api.extensions.register_dataframe_accessor("mac")
class MacAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        pass

    # general functions
    def add_diff_days(self, col_start: str, col_end: str):
        return add_diff_days(self._obj, col_start, col_end)

    def any_duplicates(self):
        return any_duplicates(self._obj)

    def assimilate(self, right: pd.DataFrame):
        return assimilate(self._obj, right)

    def diff_cols(self, right: pd.DataFrame, cols_ignore: List[str] = None):
        return diff_cols(self._obj, right, cols_ignore)

    def diff_rows(self, right: pd.DataFrame, cols_ignore: List[str] = None):
        return diff_rows(self._obj, right, cols_ignore)

    def drop_suffix(self, suffix: str):
        return drop_suffix(self._obj, suffix)

    def get_col_name(self, col_name: str):
        return get_col_name(self._obj, col_name)

    def get_col_names(self, col_names: List[str]):
        return get_col_names(self._obj, col_names)

    def is_date_col(self, arr_or_dtype):
        return is_date_col(self._obj[arr_or_dtype])

    def mark_duplicates_by_cols(self, cols: List[str]):
        return mark_duplicates_by_cols(self._obj, cols)

    def num_rows(self):
        return num_rows(self._obj)

    def num_cols(self):
        return num_cols(self._obj)

    def replace_suffix(self, old_suffix, new_suffix):
        return replace_suffix(self._obj, old_suffix, new_suffix)

    def to_datetime(self, date_col):
        return to_datetime(self._obj, date_col)

    # operators
    def filter_by_id(
        self,
        id_col: str,
        ids: List[int]
    ):
        return filter_by_id(
            self._obj,
            id_col,
            ids
        )

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
        return date_proximity(
            self._obj,
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

    def group_by_keep_one(
        self,
        group_by_col: str,
        date_col: str,
        keep: str = 'all',
        id_col: str = None,
        drop_duplicates: bool = False
    ):
        return group_by_keep_one(
            self._obj,
            group_by_col=group_by_col,
            date_col=date_col,
            keep=keep,
            id_col=id_col,
            drop_duplicates=drop_duplicates
        )
