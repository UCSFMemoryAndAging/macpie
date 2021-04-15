import openpyxl as pyxl

from . import sequence as seqtools


def keep_ws(filepath, ws_to_keep):
    wb = pyxl.load_workbook(filepath)
    ws_to_keep = seqtools.maybe_make_list(ws_to_keep)
    ws_to_delete = seqtools.diff(wb.sheetnames, ws_to_keep)
    for ws in ws_to_delete:
        del wb[ws]
    wb.save(filepath)


def move_ws_before_sheetname(filepath, ws, sheetame_pattern="-"):
    # move sheets into correct order
    wb = pyxl.load_workbook(filepath)
    insert_before_ws = next(x for x in wb.worksheets if x.title.startswith(sheetame_pattern))
    pyxl.wb_move_sheets(wb, ws, insert_before_ws.title)
    wb.save(filepath)
