import openpyxl as pyxl
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
import pandas as pd


def format_excel_cli_basic(f):
    filename = str(f)
    wb = pyxl.load_workbook(filename)

    for ws in wb.worksheets:
        if ws.title.startswith('_log_'):
            _ws_autoadjust_colwidth(ws)
        else:
            _ws_highlight_dupes(ws)

    wb.save(filename)


def format_excel_cli_link_results_with_merge(f, results_sheet=None):
    filename = str(f)
    wb = pyxl.load_workbook(filename)

    for ws in wb.worksheets:
        if ws.title.endswith('(DUPS)'):
            _ws_highlight_dupes(ws)
        elif ws.title == results_sheet:
            ws_index = wb.index(ws)
            wb.move_sheet(ws, -ws_index)
            format_multiindex(ws)
        elif ws.title.startswith('_log_'):
            _ws_autoadjust_colwidth(ws)

    wb.save(filename)


def format_multiindex(ws):
    # get row index where column A has value of 1 (index of the dataframe)
    row_index = get_row_by_col_val(ws, 0, 1)
    row_index = row_index - 1
    ws.delete_rows(row_index)

    # forced to keep the index column due to bug, so might as well give it a good name
    ws['A2'].value = "Original_Order"
    # https://stackoverflow.com/questions/54682506/openpyxl-in-python-delete-rows-function-breaks-the-merged-cell
    # ws.delete_cols(1,1)

    data_range = "A2:" + get_column_letter(ws.max_column) + str(ws.max_row)

    ws.auto_filter.ref = data_range


def read_multiindex(f):
    filename = str(f)
    wb = pyxl.load_workbook(filename)
    ws = wb.active

    if ws['A2'].value == "Original_Order":
        return pd.read_excel(filename, index_col=0, header=[0, 1], engine='openpyxl')
    else:
        return pd.read_excel(filename, index_col=None, header=[0, 1], engine='openpyxl')


def get_row_by_col_val(ws, colIndex, val):
    for row in ws.rows:
        if row[colIndex].value == val:
            return row[colIndex].row


def _ws_autoadjust_colwidth(ws):
    for column_cells in ws.columns:
        length = max(len(str(cell.value or '')) for cell in column_cells)
        length = min((length + 2) * 1.2, 65)
        ws.column_dimensions[column_cells[0].column_letter].width = length


def _ws_highlight_dupes(ws):
    dupes_col = _ws_dupes_col(ws)
    if dupes_col > -1:
        rows_iter = ws.iter_rows(min_col=dupes_col, min_row=1, max_col=dupes_col, max_row=ws.max_row)
        for row in rows_iter:
            cell = row[0]
            if cell.value is True:
                _ws_highlight_row(ws, cell.row)


def _ws_dupes_col(ws):
    for cell in ws[1]:
        if cell.value == '_duplicates':
            return cell.column
    return -1


def _ws_highlight_row(ws, row):
    rows_iter = ws.iter_rows(min_col=1, min_row=row, max_col=ws.max_column, max_row=row)
    for row in rows_iter:
        for cell in row:
            cell.fill = PatternFill("solid", fgColor="00FFFF00")
