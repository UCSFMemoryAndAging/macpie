import json

import pandas as pd
import tablib as tl

import macpie._compat as compat
from macpie._config import get_option
from macpie.tools import openpyxltools, tablibtools

from macpie.io.excel._base import (
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
    safe_xlsx_sheet_title,
    MACPieExcelReader,
    MACPieExcelWriter,
)


class MACPieOpenpyxlReader(pd.io.excel._openpyxl.OpenpyxlReader, MACPieExcelReader):
    def get_sheetname_by_index(self, index):
        return self.get_sheet_by_index(index).title

    def parse_excel_dict_sheet(self, sheet_name):
        ws = self.book.active if sheet_name is None else self.book[sheet_name]
        df = openpyxltools.worksheet_to_dataframe(ws)
        df = df.applymap(json.loads)
        dld = tablibtools.DictLikeTablibDataset.from_df(df)
        return dld.to_dict()

    def parse_tablib_dataset(
        self, sheet_name=None, headers=True, tablib_class=tablibtools.MacpieTablibDataset
    ):
        return openpyxltools.to_tablib_dataset(
            self.book, sheet_name=sheet_name, headers=headers, tablib_class=tablib_class
        )


class _MACPieOpenpyxlWriter(pd.io.excel._OpenpyxlWriter, MACPieExcelWriter):
    if compat.PANDAS_GE_15:
        _engine = "mp_openpyxl"
    else:
        engine = "mp_openpyxl"

    @property
    def sheet_names(self):
        return list(self.book.sheetnames)

    def write_excel_dict(self, excel_dict: dict):
        if excel_dict["class_name"] == "Dataset":
            sheet_name = DATASETS_SHEET_NAME
            excel_dict = {excel_dict["excel_sheetname"]: excel_dict}
        else:
            sheet_name = COLLECTION_SHEET_NAME

        dld = tablibtools.DictLikeTablibDataset.from_dict(excel_dict)

        if sheet_name in self.book.sheetnames:
            ws = self.book[sheet_name]
        else:
            ws = self.book.create_sheet()
            ws.title = sheet_name
            ws.append(dld.headers)

        for row in dld.data:
            ws.append([json.dumps(cell) for cell in row])

    def write_tablib_dataset(self, tlset: tl.Dataset, freeze_panes=True):
        ws = self.book.create_sheet()
        ws.title = (
            safe_xlsx_sheet_title(tlset.title, "-")
            if tlset.title
            else (get_option("excel.sheet_name.default"))
        )

        from tablib.formats._xlsx import XLSXFormat

        XLSXFormat.dset_sheet(tlset, ws, freeze_panes=freeze_panes)

    def highlight_duplicates(self, sheet_name, column_name):
        ws = self.book[sheet_name]
        rows_to_highlight = openpyxltools.iter_rows_with_column_value(ws, column_name, True)
        for row in rows_to_highlight:
            openpyxltools.highlight_row(ws, row)

    def finalize_sheet_order(self):
        new_sheet_order = self.finalized_sheet_order(self.sheet_names)
        self.book._sheets = [self.book[sheetname] for sheetname in new_sheet_order]

    def _autofit_column_width(self):
        for ws in self.book.worksheets:
            if ws.title.startswith("_mp"):
                openpyxltools.autofit_column_width(ws)

    if compat.PANDAS_GE_15:

        def _save(self):
            self._autofit_column_width()
            self.finalize_sheet_order()

            super()._save()

    else:

        def save(self):
            self._autofit_column_width()
            self.finalize_sheet_order()

            super().save()
