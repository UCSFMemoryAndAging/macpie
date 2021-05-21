from itertools import islice

import openpyxl as pyxl
import pandas as pd

from . import sequence as seqtools

YELLOW = "00FFFF00"


def ws_autoadjust_colwidth(ws):
    """Autoadjust the column widths of a Worksheet

    :param ws: :class:`openpyxl.worksheet.worksheet.Worksheet` to adjust
    """
    for column_cells in ws.columns:
        length = max(len(str(cell.value or '')) for cell in column_cells)
        length = min((length + 2) * 1.2, 65)
        ws.column_dimensions[column_cells[0].column_letter].width = length


def ws_get_col(ws, col_header: str = None):
    """Get column index of the ``col_header``, returning ``-1`` if not found

    :param ws: :class:`openpyxl.worksheet.worksheet.Worksheet`
    :param col_header: column header to find
    """
    if col_header is None:
        return -1

    for cell in ws[1]:
        if cell.value == col_header:
            return cell.column
    for cell in ws[2]:
        if cell.value == col_header:
            return cell.column

    return -1


def ws_get_row_by_col_val(ws, col_index, val):
    """Get row index of the first time ``val`` is found in specified column index.

    :param ws: :class:`openpyxl.worksheet.worksheet.Worksheet`
    :param col_index: column to check for ``val``
    :param val: value to find in ``col_index``
    """
    for row in ws.rows:
        if row[col_index].value == val:
            return row[col_index].row


def ws_highlight_row(ws, row: int, color: str = YELLOW):
    """Highlight row a certain color

    :param ws: :class:`openpyxl.worksheet.worksheet.Worksheet`
    :param row: row index to highlight
    :param color: color to highlight in RGB hexadecimal format (e.g. "00FFFF00"=yellow)
    """
    rows_iter = ws.iter_rows(min_col=1, min_row=row, max_col=ws.max_column, max_row=row)
    for row in rows_iter:
        for cell in row:
            cell.fill = pyxl.styles.PatternFill("solid", fgColor=color)


def ws_highlight_rows_with_col(ws, col: str, color: str = YELLOW):
    """If a cell in specified column has a value of ``True``, then highlight entire row.

    :param ws: :class:`openpyxl.worksheet.worksheet.Worksheet`
    :param col: column (header string) to check for ``True`` value
    :param color: color to highlight in RGB hexadecimal format (e.g. "00FFFF00"=yellow)
    """
    col = ws_get_col(ws, col)
    if col > -1:
        rows_iter = ws.iter_rows(min_col=col, min_row=1, max_col=col, max_row=ws.max_row)
        for row in rows_iter:
            cell = row[0]
            if cell.value is True:
                ws_highlight_row(ws, cell.row, color)


def ws_is_row_empty(ws, row_index, delete_if_empty=False):
    """Determine if a row is empty.

    :param delete_if_empty: If True, and row is empty, row is deleted.
                            defaults to False
    """
    for row in ws.iter_rows(min_row=row_index, max_row=row_index):
        empty = not any((cell.value for cell in row))
        if empty:
            if delete_if_empty:
                ws.delete_rows(row_index, 1)
            return True
    return False


def wb_move_sheets(wb, sheets_to_move, to_sheet):
    """Get row index of the first time ``val`` is found in specified column index.

    :param book: :class:`openpyxl.workbook.workbook.Workbook`
    :param sheets_to_move: list of sheetnames to move
    :param to_sheet: move sheets in ``sheets_to_move`` right before this sheetname
    """
    sheets_to_move = seqtools.maybe_make_list(sheets_to_move)
    ws_order = wb.sheetnames.copy()
    for sheetname in sheets_to_move:
        seqtools.move(ws_order, sheetname, to_sheet)
    wb._sheets = [wb[sheetname] for sheetname in ws_order]


def ws_to_df(ws, num_header: int = 1, num_idx: int = 0):
    """Converts an Excel worksheet to a :class:`pandas.DataFrame`.
    Better to use :func:`pandas.read_excel` as it takes care of a lot
    more nuances.

    :param num_header: number of header rows
    :param num_idx: number of index columns
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
