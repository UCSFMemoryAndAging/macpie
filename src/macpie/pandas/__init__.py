# flake8: noqa
from .general_df import (
    add_diff_days,
    any_duplicates,
    assimilate,
    diff_cols,
    diff_rows,
    drop_cols,
    drop_suffix,
    equals,
    flatten_multiindex,
    get_col_name,
    get_col_names,
    get_cols_by_prefixes,
    insert,
    is_date_col,
    mark_duplicates_by_cols,
    replace_suffix,
    to_datetime,
)

from .general_ser import remove_trailers

from .io import csv_to_dataframe, excel_to_dataframe, file_to_dataframe

from .multi_index import prepend_multi_index_level

from .operators.date_proximity import date_proximity
from .operators.filter_by_id import filter_by_id
from .operators.group_by_keep_one import group_by_keep_one
from .operators.merge import merge
