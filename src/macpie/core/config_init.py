"""
This module is imported from the macpie package __init__.py file
in order to ensure that the core.config options registered here will
be available as soon as the user loads the package. If register_option
is invoked inside specific modules, they will not be registered until that
module is imported, which may or may not be a problem.

If you need to make sure options are available even before a certain
module is imported, register them here rather than in the module.
"""

import pandas._config.config as pandas_cf
from pandas import options as pandas_options

import macpie._config.config as cf

# set pandas options
pandas_options.io.excel.xlsx.writer = "xlsxwriter"


# set macpie options
cf.register_option("dataset.default.name", "NO_NAME", "", validator=pandas_cf.is_str)

cf.register_option("dataset.id_col_name", "InstrID", "", validator=pandas_cf.is_str)

cf.register_option("dataset.date_col_name", "DCDate", "", validator=pandas_cf.is_str)

cf.register_option("dataset.id2_col_name", "PIDN", "", validator=pandas_cf.is_str)


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
    lambda: cf.get_option("column.system.prefix") + "_abs_diff_days",
    "",
    validator=pandas_cf.is_str,
)

cf.register_option(
    "column.system.diff_days",
    lambda: cf.get_option("column.system.prefix") + "_diff_days",
    "",
    validator=pandas_cf.is_str,
)

cf.register_option(
    "column.system.duplicates",
    lambda: cf.get_option("column.system.prefix") + "_duplicates",
    "",
    validator=pandas_cf.is_str,
)

cf.register_option(
    "column.system.merge",
    lambda: cf.get_option("column.system.prefix") + "_merge",
    "",
    validator=pandas_cf.is_str,
)

cf.register_option("excel.writer.engine", "mp_xlsxwriter", "", validator=pandas_cf.is_str)

cf.register_option("excel.row_index_header", "Original_Order", "", validator=pandas_cf.is_str)

cf.register_option("excel.sheet_name.default", "_mp_sheet", "", validator=pandas_cf.is_str)

cf.register_option(
    "operators.binary.column_suffixes", ("_x", "_y"), "", validator=cf.is_tuple_of_two
)
