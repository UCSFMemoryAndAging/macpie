import json

import pandas as pd
import tablib as tl

from macpie._config import get_option
from macpie import lltools, openpyxltools, tablibtools

from ._base import (
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
    safe_xlsx_sheet_title,
    MACPieExcelReader,
    MACPieExcelWriter,
)


class MACPieOpenpyxlReader(MACPieExcelReader, pd.io.excel._openpyxl.OpenpyxlReader):
    def parse_excel_dict(self, sheet_name, headers=True):
        ws = self.book.active if sheet_name is None else self.book[sheet_name]
        df = openpyxltools.to_df(ws)
        df = df.applymap(json.loads)
        dld = tablibtools.DictLikeDataset.from_df(df)
        return dld.to_dict()

    def parse_tablib_dataset(self, sheet_name, headers=True):
        ws = self.book.active if sheet_name is None else self.book[sheet_name]
        return openpyxltools.to_tablib_dataset(ws)

    def parse_simple_dataset(self, sheet_name, headers=True):
        tlset = self.parse_tablib_dataset(sheet_name, headers)
        return tablibtools.SimpleDataset.from_tlset(tlset)

    def parse_dictlike_dataset(self, sheet_name, headers=True):
        tlset = self.parse_tablib_dataset(sheet_name, headers)
        return tablibtools.DictLikeDataset.from_tlset(tlset)

    def parse_multiindex_df(self, sheet_name):
        ws = self.book[sheet_name]
        if ws["A2"].value == get_option("excel.row_index_header"):
            return self.parse(sheet_name=sheet_name, index_col=0, header=[0, 1])
        else:
            return self.parse(sheet_name=sheet_name, index_col=None, header=[0, 1])

    def parse_multiindex_dataset(self, sheet_name, excel_dict):
        from macpie import Dataset

        df = self.parse_multiindex_df(sheet_name)
        dset = Dataset.from_excel_dict(excel_dict, df)
        return dset


class _MACPieOpenpyxlWriter(MACPieExcelWriter, pd.io.excel._OpenpyxlWriter):
    def write_excel_dict(self, excel_dict: dict):
        if excel_dict["class_name"] == "Dataset":
            sheet_name = DATASETS_SHEET_NAME
            excel_dict = {excel_dict["excel_sheetname"]: excel_dict}
        else:
            sheet_name = COLLECTION_SHEET_NAME

        dld = tablibtools.DictLikeDataset.from_dict(excel_dict)

        if sheet_name in self.book.sheetnames:
            ws = self.book[sheet_name]
        else:
            ws = self.book.create_sheet()
            ws.title = sheet_name
            ws.append(dld.headers)

        for row in dld.data:
            ws.append([json.dumps(cell) for cell in row])

    def write_tablib_dataset(self, tlset: tl.Dataset):
        ws = self.book.create_sheet()
        ws.title = (
            safe_xlsx_sheet_title(tlset.title, "-")
            if tlset.title
            else (get_option("excel.sheet_name.default"))
        )

        from tablib.formats._xlsx import XLSXFormat

        XLSXFormat.dset_sheet(tlset, ws)

    def write_simple_dataset(self, simple_dataset: tablibtools.SimpleDataset):
        self.write_tablib_dataset(simple_dataset.tlset)

    def handle_multiindex(self, sheet_name):
        ws = self.book[sheet_name]
        if openpyxltools.is_row_empty(ws, row_index=3, delete_if_empty=True):
            # Special case to handle pandas and openpyxl bugs when writing
            # dataframes with multiindex.
            # https://stackoverflow.com/questions/54682506/openpyxl-in-python-delete-rows-function-breaks-the-merged-cell
            # https://github.com/pandas-dev/pandas/issues/27772
            # Another openpyxl bug where if number of index cols > 1,
            # deleting rows doesn't work if adjacent cells in the index have been merged.
            # Since we are forced to keep the index column due to bug,
            # might as well give it an informative name
            ws["A2"].value = get_option("excel.row_index_header")

    def highlight_duplicates(self, sheet_name, column_name):
        ws = self.book[sheet_name]
        rows_to_highlight = openpyxltools.iter_rows_with_column_value(ws, column_name, True)
        for row in rows_to_highlight:
            openpyxltools.highlight_row(ws, row)

    def reorder_sheets(self):
        try:
            sheetnames = list(self.book.sheetnames)
            dset_sheet_index = sheetnames.index(DATASETS_SHEET_NAME) + 1
            sheetname_to_move_to = next(
                sheetname
                for sheetname in sheetnames[dset_sheet_index:]
                if sheetname.startswith("_mp")
            )
            lltools.move_item_to(sheetnames, DATASETS_SHEET_NAME, sheetname_to_move_to)
            self.book._sheets = [self.book[sheetname] for sheetname in sheetnames]
        except (ValueError, StopIteration) as e:
            pass

    def save(self):
        for ws in self.book.worksheets:
            if ws.title.startswith("_mp"):
                openpyxltools.autoadjust_column_widths(ws)

        self.reorder_sheets()

        super().save()
