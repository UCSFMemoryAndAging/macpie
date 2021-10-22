import openpyxl
import pandas as pd
import tablib as tl


def read_excel(filepath, sheet_name: str = None, headers=True):
    """Returns a Tablib Dataset from an Excel file."""

    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    sheet = wb.active if sheet_name is None else wb[sheet_name]

    dset = tl.Dataset()
    dset.title = sheet.title

    for i, row in enumerate(sheet.rows):
        row_vals = [c.value for c in row]
        if (i == 0) and (headers):
            dset.headers = row_vals
        else:
            dset.append(row_vals)

    return dset
