# flake8: noqa

from macpie.pandas.combine import date_proximity, merge

from macpie.pandas.compare import compare, diff_cols, diff_rows, equals

from macpie.pandas.convert import conform, mimic_dtypes, mimic_index_order, to_datetime

from macpie.pandas.describe import (
    add_diff_days,
    any_duplicates,
    count_trailers,
    is_date_col,
    mark_duplicates_by_cols,
)

from macpie.pandas.groupby import group_by_keep_one

from macpie.pandas.io import read_csv, read_excel, read_file

from macpie.pandas.indexing import (
    drop_suffix,
    flatten_multiindex,
    insert,
    prepend_multi_index_level,
    replace_suffix,
)

from macpie.pandas.select import (
    filter_by_id,
    filter_labels,
    filter_labels_pair,
    get_col_name,
    get_col_names,
    get_cols_by_prefixes,
    remove_trailers,
    rtrim,
    rtrim_longest,
    subset,
    subset_pair,
)

from macpie.pandas.sort import sort_values_pair
