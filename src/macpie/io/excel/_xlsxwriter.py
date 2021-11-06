import json

import pandas as pd
import tablib as tl

from macpie._config import get_option
from macpie import tablibtools

from ._base import (
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
    safe_xlsx_sheet_title,
    MACPieExcelWriter,
)


class _MACPieXlsxWriter(MACPieExcelWriter, pd.io.excel._XlsxWriter):
    engine = "mp_xlsxwriter"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # track for post-processing
        self.dup_sheets = {}

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
            ws = self.book.add_worksheet(sheet_name)
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

        ws = self.book.add_worksheet(sheet_name)

        _package = tlset._package(dicts=False)

        for i, sep in enumerate(tlset._separators):
            _offset = i
            _package.insert((sep[0] + _offset), (sep[1],))

        for i, row in enumerate(_package):
            row_number = i + 1
            for j, col in enumerate(row):
                ws.write(i, j, col)

                # bold headers
                if (row_number == 1) and tlset.headers:
                    ws.write(i, j, col, self.format_bold)
                    if freeze_panes:
                        # Freeze only after first line
                        ws.freeze_panes("A2")

                # bold separators
                elif len(row) < tlset.width:
                    ws.write(i, j, col, self.format_bold)

                # wrap the rest
                else:
                    try:
                        str_col_value = str(col)
                    except TypeError:
                        str_col_value = ""

                    if "\n" in str_col_value:
                        ws.write(i, j, col, self.format_text_wrap)
                    else:
                        ws.write(i, j, col)

    def highlight_duplicates(self, sheet_name, column_name):
        raise NotImplementedError

    def finalize_sheet_order(self):
        new_sheet_order = self.finalized_sheet_order(self.sheet_names())
        self.book.worksheets_objs.sort(key=lambda x: new_sheet_order.index(x.name))

    def save(self):
        self.finalize_sheet_order()
        super().save()
