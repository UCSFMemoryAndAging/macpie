import openpyxl as pyxl
from openpyxl.styles import PatternFill


def format_excel(f):
    filename = str(f)
    wb = pyxl.load_workbook(filename)
    for ws in wb.worksheets:
        if ws.title.startswith('_log_'):
            _ws_autoadjust_colwidth(ws)
            ws.sheet_state = 'hidden'
        else:
            _ws_highlight_dupes(ws)
    wb.save(filename)


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
