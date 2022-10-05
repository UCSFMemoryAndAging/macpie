import json

import pandas as pd
import tablib as tl
import xlsxwriter

import macpie._compat as compat
from macpie._config import get_option
from macpie.io.excel._base import (
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
    safe_xlsx_sheet_title,
    MACPieExcelWriter,
)
from macpie.tools import tablibtools, xlsxwritertools


class _MACPieXlsxWriter(pd.io.excel._XlsxWriter, MACPieExcelWriter):
    if compat.PANDAS_GE_15:
        _engine = "mp_xlsxwriter"
    else:
        engine = "mp_xlsxwriter"

    def __init__(
        self,
        path,
        engine=None,
        date_format=None,
        datetime_format=None,
        mode: str = "w",
        storage_options=None,
        if_sheet_exists=None,
        engine_kwargs=None,
        **kwargs,
    ):
        super().__init__(
            path,
            engine=engine,
            date_format=date_format,
            datetime_format=datetime_format,
            mode=mode,
            storage_options=storage_options,
            if_sheet_exists=if_sheet_exists,
            engine_kwargs=engine_kwargs,
        )

        engine_kwargs = pd.io.excel._util.combine_kwargs(engine_kwargs, kwargs)

        if compat.PANDAS_GE_15:
            self._book = MACPieXlsxWriterWorkbook(self._handles.handle, **engine_kwargs)
        else:
            self.book = MACPieXlsxWriterWorkbook(self.handles.handle, **engine_kwargs)

        self.format_bold = self.book.add_format({"bold": True})
        self.format_text_wrap = self.book.add_format({"text_wrap": True})

    def sheet_names(self):
        return list(self.book.sheetnames)

    def write_excel_dict(self, excel_dict: dict):
        if excel_dict["class_name"] == "Dataset":
            sheet_name = DATASETS_SHEET_NAME
            excel_dict = {excel_dict["excel_sheetname"]: excel_dict}
        else:
            sheet_name = COLLECTION_SHEET_NAME

        dld = tablibtools.DictLikeTablibDataset.from_dict(excel_dict)

        ws = self.book.get_worksheet_by_name(sheet_name)

        if ws is None:
            ws = self.book.add_worksheet(sheet_name, autofit_columns=True)
            ws.write_row("A1", dld.headers, self.format_bold)

        row_index = ws.dim_rowmax + 1
        for row in dld.data:
            ws.write_row(row_index, 0, [json.dumps(cell) for cell in row])
            row_index += 1

    def write_tablib_dataset(self, tlset: tl.Dataset, freeze_panes=True):
        sheet_name = (
            safe_xlsx_sheet_title(tlset.title, "-")
            if tlset.title
            else (get_option("excel.sheet_name.default"))
        )

        ws = self.book.add_worksheet(sheet_name, autofit_columns=True)

        xlsxwritertools.tlset_sheet(
            tlset, ws, self.format_bold, self.format_text_wrap, freeze_panes=freeze_panes
        )

    def highlight_duplicates(self, sheet_name, column_name):
        raise NotImplementedError

    def finalize_sheet_order(self):
        new_sheet_order = self.finalized_sheet_order(self.sheet_names())
        self.book.worksheets_objs.sort(key=lambda x: new_sheet_order.index(x.name))

    if compat.PANDAS_GE_15:

        def _save(self):
            self.finalize_sheet_order()

            super()._save()

    else:

        def save(self):
            self.finalize_sheet_order()

            super().save()


class MACPieXlsxWriterWorkbook(xlsxwriter.workbook.Workbook):
    def __init__(self, filename=None, options=None):
        if options is None:
            options = {}

        self.autofit_columns = options.pop("autofit_columns", False)
        self.strip_carriage_returns = options.pop("strip_carriage_returns", False)

        super().__init__(filename=filename, options=options)

    def add_worksheet(
        self, name=None, worksheet_class=None, autofit_columns=None, strip_carriage_returns=None
    ):
        if worksheet_class is not None:
            return super().add_worksheet(name, worksheet_class=worksheet_class)

        worksheet = super().add_worksheet(name, worksheet_class=MACPieXlsxWriterWorksheet)
        worksheet.autofit_columns = autofit_columns if autofit_columns else self.autofit_columns
        worksheet.strip_carriage_returns = (
            strip_carriage_returns if strip_carriage_returns else self.strip_carriage_returns
        )

        return worksheet

    def close(self):
        for worksheet in self.worksheets():
            if hasattr(worksheet, "autofit_columns") and worksheet.autofit_columns is True:
                # Apply stored column widths. This will override any other
                # set_column() values that may have been applied.
                worksheet.set_autofit_column_width()

        return super().close()


class MACPieXlsxWriterWorksheet(xlsxwriter.worksheet.Worksheet):
    def __init__(self):
        super().__init__()

        # Store column widths
        self.max_column_widths = {}

    def set_autofit_column_width(self):
        for column, width in self.max_column_widths.items():
            self.set_column(column, column, width)

    def do_autofit_column_width(self, row, col, string, cell_format=None):
        # Store the maximum string width seen in each column.

        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        def excel_string_width(str):
            """Calculate the length of the string in Excel character units."""

            string_width = len(str)

            if string_width == 0:
                return 0
            else:
                return string_width * 1.1

        # Set the min width for the cell. In some cases this might be the
        # default width of 8.43. In this case we use 0 and adjust for all
        # string widths.
        min_width = 0

        # Check if it the string is the largest we have seen for this column.
        string_width = excel_string_width(string)
        if string_width > min_width:
            max_width = self.max_column_widths.get(col, min_width)
            if string_width > max_width:
                self.max_column_widths[col] = string_width

    def do_strip_carriage_returns(self, row, col, string, cell_format=None):
        if "\r" in string:
            return string.replace("\r", "")
        return string

    def _write_string(self, row, col, string, cell_format=None):
        if self.strip_carriage_returns:
            string = self.do_strip_carriage_returns(row, col, string, cell_format)

        if self.autofit_columns:
            self.do_autofit_column_width(row, col, string, cell_format)

        return super()._write_string(row, col, string, cell_format)
