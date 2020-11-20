from itertools import islice

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


def ws_highlight_rows_with_col(ws, col):
    col = ws_get_col(ws, col)
    if col > -1:
        rows_iter = ws.iter_rows(min_col=col, min_row=1, max_col=col, max_row=ws.max_row)
        for row in rows_iter:
            cell = row[0]
            if cell.value is True:
                ws_highlight_row(ws, cell.row)


def ws_to_df(ws, num_header: int = 1, num_idx: int = 0):
    """Better to use pandas.read_excel as it takes care of a lot more nuances
    """
    if num_header == 1 and num_idx == 0:
        return _ws_to_df_default(ws)

    data = ws.values

    if num_header == 1:
        cols = next(data)[num_idx:]
    elif num_header > 1:
        col_tuples = []
        for x in range(num_header):
            col_tuples.append(next(data)[num_idx:])
        zipped = zip(*col_tuples)
        cols = pd.MultiIndex.from_tuples(list(zipped))
    else:
        cols = None

    data = list(data)

    if num_idx > 0:
        if num_idx == 1:
            idx = [r[0] for r in data]
        else:
            tuples = [r[:num_idx] for r in data]
            idx = pd.MultiIndex.from_tuples(tuples)
        data = (islice(r, num_idx, None) for r in data)
        df = pd.DataFrame(data, index=idx, columns=cols)
    else:
        df = pd.DataFrame(data, columns=cols)

    return df


def _ws_to_df_default(ws):
    data = ws.values
    cols = next(data)
    df = pd.DataFrame(data, columns=cols)
    return df
