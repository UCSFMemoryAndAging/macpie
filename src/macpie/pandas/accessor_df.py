from typing import List

import pandas as pd

from macpie._config import get_option

from . import general_df
from . import multi_index
from . import operators


@pd.api.extensions.register_dataframe_accessor("mac")
class MacDataFrameAccessor:
    """
    Custom DataFrame accessor to extend the :class:`pandas.DataFrame` object.
    This creates an additional namepace on the DataFrame object called ``mac``.

    All methods exposed via this accessor are derived from functions already
    available via the public API, leaving out the first DataFrame argument.
    This is essentially syntactic sugar for calling those functions.
    """

    def __init__(self, df):
        self._validate(df)
        self._df = df

    @staticmethod
    def _validate(obj):
        pass

    # general functions
    def add_diff_days(
        self, col_start: str, col_end: str, diff_days_col: str = None, inplace=False
    ):
        """see :meth:`macpie.pandas.add_diff_days`"""
        return general_df.add_diff_days(
            self._df, col_start, col_end, diff_days_col=diff_days_col, inplace=inplace
        )

    def any_duplicates(self, col: str, ignore_nan: bool = False):
        """see :meth:`macpie.pandas.any_duplicates`"""
        return general_df.any_duplicates(self._df, col, ignore_nan=ignore_nan)

    def assimilate(self, right: pd.DataFrame):
        """see :meth:`macpie.pandas.assimilate`"""
        return general_df.assimilate(self._df, right)

    def col_count(self):
        """see :meth:`macpie.pandas.num_cols`"""
        return len(self._df.columns)

    def diff_cols(self, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat=None):
        """see :meth:`macpie.pandas.diff_cols`"""
        return general_df.diff_cols(
            self._df, right, cols_ignore=cols_ignore, cols_ignore_pat=cols_ignore_pat
        )

    def diff_rows(self, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat=None):
        """see :meth:`macpie.pandas.diff_rows`"""
        return general_df.diff_rows(
            self._df, right, cols_ignore=cols_ignore, cols_ignore_pat=cols_ignore_pat
        )

    def drop_cols(self, cols_list=set(), cols_pat=None):
        """see :meth:`macpie.pandas.drop_cols`"""
        return general_df.drop_cols(self._df, cols_list=cols_list, cols_pat=cols_pat)

    def drop_suffix(self, suffix: str):
        """see :meth:`macpie.pandas.drop_suffix`"""
        return general_df.drop_suffix(self._df, suffix)

    def equals(self, right: pd.DataFrame, cols_ignore=set(), cols_ignore_pat=None):
        """see :meth:`macpie.pandas.equals`"""
        return general_df.equals(
            self._df, right, cols_ignore=cols_ignore, cols_ignore_pat=cols_ignore_pat
        )

    def flatten_multiindex(self, axis: int = 0, delimiter: str = "_"):
        """see :meth:`macpie.pandas.flatten_multiindex`"""
        return general_df.flatten_multiindex(self._df, axis=axis, delimiter=delimiter)

    def get_col_name(self, col_name: str):
        """see :meth:`macpie.pandas.get_col_name`"""
        return general_df.get_col_name(self._df, col_name)

    def get_col_names(self, col_names: List[str], strict=True):
        """see :meth:`macpie.pandas.get_col_names`"""
        return general_df.get_col_names(self._df, col_names, strict=strict)

    def get_cols_by_prefixes(self, prefixes: List[str], one_match_only=True):
        """see :meth:`macpie.pandas.get_cols_by_prefixes`"""
        return general_df.get_cols_by_prefixes(self._df, prefixes, one_match_only=one_match_only)

    def insert(self, col_name, col_value, allow_duplicates=False):
        """see :meth:`macpie.pandas.insert`"""
        return general_df.insert(self._df, col_name, col_value, allow_duplicates=allow_duplicates)

    def is_date_col(self, arr_or_dtype):
        """see :meth:`macpie.pandas.is_date_col`"""
        return general_df.is_date_col(self._df[arr_or_dtype])

    def mark_duplicates_by_cols(self, cols: List[str]):
        """see :meth:`macpie.pandas.mark_duplicates_by_cols`"""
        return general_df.mark_duplicates_by_cols(self._df, cols)

    def prepend_multi_index_level(self, level_name: str, axis: int = 0):
        return multi_index.prepend_multi_index_level(self._df, level_name, axis=axis)

    def replace_suffix(self, old_suffix, new_suffix):
        """see :meth:`macpie.pandas.replace_suffix`"""
        return general_df.replace_suffix(self._df, old_suffix, new_suffix)

    def row_count(self):
        """see :meth:`macpie.pandas.num_rows`"""
        return len(self._df.index)

    def to_datetime(self, date_col_name):
        """see :meth:`macpie.pandas.to_datetime`"""
        return general_df.to_datetime(self._df, date_col_name)

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
        get: str = "all",
        when: str = "earlier_or_later",
        days: int = 90,
        left_link_id=None,
        dropna: bool = False,
        drop_duplicates: bool = False,
        duplicates_indicator: bool = False,
        merge="partial",
        merge_suffixes=get_option("operators.binary.column_suffixes"),
    ):
        """see :meth:`macpie.pandas.date_proximity`"""
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
            drop_duplicates=drop_duplicates,
            duplicates_indicator=duplicates_indicator,
            merge=merge,
            merge_suffixes=merge_suffixes,
        )

    def filter_by_id(self, id_col_name: str, ids: List[int]):
        """see :meth:`macpie.pandas.filter_by_id`"""
        return operators.filter_by_id.filter_by_id(self._df, id_col_name, ids)

    def group_by_keep_one(
        self,
        group_by_col: str,
        date_col_name: str,
        keep: str = "all",
        id_col_name: str = None,
        drop_duplicates: bool = False,
    ):
        """see :meth:`macpie.pandas.group_by_keep_one`"""
        return operators.group_by_keep_one.group_by_keep_one(
            self._df,
            group_by_col=group_by_col,
            date_col_name=date_col_name,
            keep=keep,
            id_col_name=id_col_name,
            drop_duplicates=drop_duplicates,
        )

    def merge(
        self,
        right: pd.DataFrame,
        on=None,
        left_on=None,
        right_on=None,
        merge_suffixes=get_option("operators.binary.column_suffixes"),
        add_suffixes=False,
        add_indexes=(None, None),
    ):
        """see :meth:`macpie.pandas.merge`"""
        return operators.merge.merge(
            self._df,
            right,
            on=on,
            left_on=left_on,
            right_on=right_on,
            merge_suffixes=merge_suffixes,
            add_suffixes=add_suffixes,
            add_indexes=add_indexes,
        )
