import copy
from pathlib import Path
import re

import openpyxl as pyxl

from macpie import openpyxltools
from macpie.testing import assert_excel_worksheet_equal


THIS_DIR = Path(__file__).parent.absolute()


def test_replace():

    wb = pyxl.load_workbook(THIS_DIR / "data.xlsx")

    # only work with copy as it will be modified in place
    orig_ws = wb["data"]

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="2", value=99)
    assert_excel_worksheet_equal(ws, wb["str;2->99"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="-3", value=98)
    assert_excel_worksheet_equal(ws, wb["str;-3->98"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="2|\-3", value=99, regex=True)
    assert_excel_worksheet_equal(ws, wb["re;2,-3->99"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="-[3,4]", value=99, regex=True)
    assert_excel_worksheet_equal(ws, wb["re;-3,-4->99"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="apple", value="orange", regex=True)
    assert_excel_worksheet_equal(ws, wb["str;apple->orange"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="Apple", value="orange", regex=True, ignorecase=True)
    assert_excel_worksheet_equal(ws, wb["str;Apple->orange;ignorecase"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace="This is a\nmultiline sentence.", value="")
    assert_excel_worksheet_equal(ws, wb["str;multiline"])

    ws = copy.deepcopy(orig_ws)
    openpyxltools.replace(ws, to_replace=".*multiline.*", value="", regex=True, flags=re.DOTALL)
    assert_excel_worksheet_equal(ws, wb["str;multiline;dotall"])

    # wb.save(current_dir / "result.xlsx")
