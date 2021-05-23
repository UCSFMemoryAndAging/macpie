"""
This module is imported from the pandas package __init__.py file
in order to ensure that the core.config options registered here will
be available as soon as the user loads the package. If register_option
is invoked inside specific modules, they will not be registered until that
module is imported, which may or may not be a problem.

If you need to make sure options are available even before a certain
module is imported, register them here rather than in the module.
"""

import pandas._config.config as pandas_cf

import macpie._config.config as cf


# set pandas options
# from pandas import options  # noqa: E402
# options.io.excel.xlsx.writer = "xlsxwriter"
# thought xlsxwriter would be faster than openpyxl, but it's not


# set macpie options
cf.register_option(
    "dataset.id_col", "InstrID", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.date_col", "DCDate", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.id2_col", "PIDN", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.tag.anchor", "anchor", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.tag.duplicates", "duplicates", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.tag.mergeable", "mergeable", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.tag.merged", "merged", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.tag.not_merged", "not_merged", "", validator=pandas_cf.is_str
)

cf.register_option(
    "dataset.tag.secondary", "secondary", "", validator=pandas_cf.is_str
)


def set_system_columns_cb(key):
    cf.reset_option("column.system.abs_diff_days")
    cf.reset_option("column.system.diff_days")
    cf.reset_option("column.system.duplicates")
    cf.reset_option("column.system.merge")


cf.register_option(
    "column.system.prefix", "_mp", "", validator=pandas_cf.is_str, cb=set_system_columns_cb
)

cf.register_option(
    "column.system.abs_diff_days",
    lambda: cf.get_option("column.system.prefix") + "_abs_diff_days" ,
    "",
    validator=pandas_cf.is_str
)

cf.register_option(
    "column.system.diff_days",
    lambda: cf.get_option("column.system.prefix") + "_diff_days",
    "",
    validator=pandas_cf.is_str
)

cf.register_option(
    "column.system.duplicates",
    lambda: cf.get_option("column.system.prefix") + "_duplicates",
    "",
    validator=pandas_cf.is_str
)

cf.register_option(
    "column.system.merge",
    lambda: cf.get_option("column.system.prefix") + "_merge",
    "",
    validator=pandas_cf.is_str
)

cf.register_option(
    "column.dataset", "Dataset", "", validator=pandas_cf.is_str
)

cf.register_option(
    "column.field", "Field", "", validator=pandas_cf.is_str
)

cf.register_option(
    "column.link_id", "link_id", "", validator=pandas_cf.is_str
)

cf.register_option(
    "column.to_merge", "Merge?", "", validator=pandas_cf.is_str
)

cf.register_option(
    "excel.row_index_header", "Original_Order", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.available_fields", "_available_fields", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.client_system_info", "_sys_info", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.command_info", "_cmd_info", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.collection_info", "_dsets_info", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.dsets_history", "_dsets_history", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.default", "_mp_sheet", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.merged_results", "MERGED_RESULTS", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.name.selected_fields", "_selected_fields", "", validator=pandas_cf.is_str
)

cf.register_option(
    "sheet.suffix.duplicates", "_DUPS", "", validator=pandas_cf.is_str
)

cf.register_option(
    "operators.binary.column_suffixes", ("_x", "_y"), "", validator=cf.is_tuple_of_two
)
