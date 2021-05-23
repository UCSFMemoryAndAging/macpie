"""
Utilities for conversion to writer-agnostic Excel representation.
"""

import re

import pandas as pd
import tablib as tl

from macpie._config import get_option
from macpie.tools import openpyxl as openpyxltools


INVALID_TITLE_REGEX = re.compile(r'[\\*?:/\[\]]')


def safe_xlsx_sheet_title(s, replace="-"):
    return re.sub(INVALID_TITLE_REGEX, replace, s)[:31]


class MACPieExcelFormatter(pd.io.formats.excel.ExcelFormatter):

    def __init__(self, dset, **kwargs):
        self.dset = dset
        super().__init__(dset.df, **kwargs)

    def write(
        self,
        writer,
        sheet_name=None,
        startrow=0,
        startcol=0,
        freeze_panes=None,
        engine=None,
        storage_options: pd._typing.StorageOptions = None,
    ):
        """
        writer : path-like, file-like, or ExcelWriter object
            File path or existing ExcelWriter
        sheet_name : string, default 'Sheet1'
            Name of sheet which will contain DataFrame
        startrow :
            upper left cell row to dump data frame
        startcol :
            upper left cell column to dump data frame
        freeze_panes : tuple of integer (length 2), default None
            Specifies the one-based bottommost row and rightmost column that
            is to be frozen
        engine : string, default None
            write engine to use if writer is a path - you can also set this
            via the options ``io.excel.xlsx.writer``, ``io.excel.xls.writer``,
            and ``io.excel.xlsm.writer``.
            .. deprecated:: 1.2.0
                As the `xlwt <https://pypi.org/project/xlwt/>`__ package is no longer
                maintained, the ``xlwt`` engine will be removed in a future
                version of pandas.
        {storage_options}
            .. versionadded:: 1.2.0
        """
        num_rows, num_cols = self.df.shape
        if num_rows > self.max_rows or num_cols > self.max_cols:
            raise ValueError(
                f"This sheet is too large! Your sheet size is: {num_rows}, {num_cols} "
                f"Max sheet size is: {self.max_rows}, {self.max_cols}"
            )

        formatted_cells = self.get_formatted_cells()
        if isinstance(writer, pd.io.excel.ExcelWriter):
            need_save = False
        else:
            # pandas\io\formats\excel.py:808: error: Cannot instantiate
            # abstract class 'ExcelWriter' with abstract attributes 'engine',
            # 'save', 'supported_extensions' and 'write_cells'  [abstract]
            writer = MACPieExcelWriter(  # type: ignore[abstract]
                writer, engine=engine, storage_options=storage_options
            )
            need_save = True

        if sheet_name is None:
            sheet_name = self.dset.get_excel_sheetname()

        try:
            writer.write_cells(
                formatted_cells,
                sheet_name=get_option("sheet.name.default") if sheet_name is None else sheet_name,
                startrow=startrow,
                startcol=startcol,
                freeze_panes=freeze_panes,
            )
        finally:
            # make sure to close opened file handles
            if need_save:
                writer.close()


class MACPieExcelWriter(pd.io.excel._OpenpyxlWriter):
    engine = 'openpyxl'
    supported_extensions = ('xlsx',)

    def write_cells(self,
                    cells,
                    sheet_name=None,
                    startrow=0,
                    startcol=0,
                    freeze_panes=None):
        super().write_cells(cells,
                            sheet_name=sheet_name,
                            startrow=startrow,
                            startcol=startcol,
                            freeze_panes=freeze_panes)

    def write_tlset(self, tlset: tl.Dataset):
        ws = self.book.create_sheet()
        ws.title = (
            safe_xlsx_sheet_title(tlset.title, '-')
            if tlset.title else (get_option("sheet.name.default"))
        )
        from tablib.formats._xlsx import XLSXFormat
        XLSXFormat.dset_sheet(tlset, ws)

    def save(self):
        for ws in self.book.worksheets:
            if ws.title.startswith('_'):
                openpyxltools.ws_autoadjust_colwidth(ws)
            if ws.title == get_option("sheet.name.merged_results"):
                if openpyxltools.ws_is_row_empty(ws, row_index=3, delete_if_empty=True):
                    # Special case to handle pandas and openpyxl bugs when writing
                    # dataframes with multiindex.
                    # https://stackoverflow.com/questions/54682506/openpyxl-in-python-delete-rows-function-breaks-the-merged-cell
                    # https://github.com/pandas-dev/pandas/issues/27772
                    # Another openpyxl bug where if number of index cols > 1,
                    # deleting rows doesn't work if adjacent cells in the index have been merged.
                    # Since we are forced to keep the index column due to bug,
                    # might as well give it an informative name
                    ws['A2'].value = get_option("excel.row_index_header")
            if (
                    ws.title.endswith(get_option("dataset.tag.duplicates"))
                    or ws.title.endswith(get_option("sheet.suffix.duplicates"))
            ):
                openpyxltools.ws_highlight_rows_with_col(ws, get_option("column.system.duplicates"))

        super().save()


pd.io.excel.register_writer(MACPieExcelWriter)
