import json

import pandas as pd
import tablib as tl
import xlsxwriter

from macpie._config import get_option
from macpie import tablibtools, xlsxwritertools

from ._base import (
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
    safe_xlsx_sheet_title,
    MACPieExcelWriter,
)


class _MACPieXlsxWriter(pd.io.excel._XlsxWriter, MACPieExcelWriter):
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

        dld = tablibtools.DictLikeDataset.from_dict(excel_dict)

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

    def save(self):
        self.finalize_sheet_order()

        super().save()


class MACPieXlsxWriterWorkbook(xlsxwriter.workbook.Workbook):
    def add_worksheet(self, name=None, worksheet_class=None, autofit_columns=False):
        if autofit_columns:
            worksheet = super().add_worksheet(
                name, worksheet_class=xlsxwritertools.XlsxWriterAutofitColumnsWorksheet
            )
        else:
            worksheet = super().add_worksheet(name, worksheet_class=worksheet_class)

        return worksheet

    def close(self):
        for worksheet in self.worksheets():
            if type(worksheet) is xlsxwritertools.XlsxWriterAutofitColumnsWorksheet:
                # Apply stored column widths. This will override any other
                # set_column() values that may have been applied.
                worksheet.set_autofit_column_width()

        return super().close()
