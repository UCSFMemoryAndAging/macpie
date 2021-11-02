from ._base import (
    MACPieExcelFile,
    MACPieExcelWriter,
    read_excel,
    safe_xlsx_sheet_title,
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
)
from ._openpyxl import _MACPieOpenpyxlWriter
from ._xlsxwriter import _MACPieXlsxWriter

__all__ = [
    "MACPieExcelFile",
    "MACPieExcelWriter",
    "read_excel",
    "safe_xlsx_sheet_title",
    "DATASETS_SHEET_NAME",
    "COLLECTION_SHEET_NAME",
]

import pandas

pandas.io.excel.register_writer(_MACPieOpenpyxlWriter)

pandas.io.excel.register_writer(_MACPieXlsxWriter)
