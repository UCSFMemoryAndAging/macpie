from openpyxl.styles import PatternFill
import pandas as pd


def get_row_by_col_val(ws, col_index, val):
    for row in ws.rows:
        if row[col_index].value == val:
            return row[col_index].row


def ws_autoadjust_colwidth(ws):
    for column_cells in ws.columns:
        length = max(len(str(cell.value or '')) for cell in column_cells)
        length = min((length + 2) * 1.2, 65)
        ws.column_dimensions[column_cells[0].column_letter].width = length


def ws_get_col(ws, col_header: str = None):
    if col_header is None:
        return -1

    for cell in ws[1]:
        if cell.value == col_header:
            return cell.column
    for cell in ws[2]:
        if cell.value == col_header:
            return cell.column

    return -1


def ws_highlight_row(ws, row):
    rows_iter = ws.iter_rows(min_col=1, min_row=row, max_col=ws.max_column, max_row=row)
    for row in rows_iter:
        for cell in row:
            cell.fill = PatternFill("solid", fgColor="00FFFF00")


def ws_to_df(ws):
    data = ws.values
    cols = next(data)
    df = pd.DataFrame(data, columns=cols)
    return df
