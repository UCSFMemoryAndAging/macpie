import copy
from pathlib import Path

import openpyxl as pyxl

from macpie.pandas.io import file_to_dataframe
from macpie.testing import assert_excel_worksheet_equal

from macpie import openpyxltools

current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None


def test_replace():

    wb = pyxl.load_workbook(current_dir / "data.xlsx")

    # only work with copy as it will be modified in place
    orig_ws = wb["data"]

    ws = copy.deepcopy(orig_ws)
    expected_ws = wb["2->99"]
    openpyxltools.replace(ws, to_replace="2", value=99)
    assert_excel_worksheet_equal(ws, expected_ws)

    ws = copy.deepcopy(orig_ws)
    expected_ws = wb["-3->98"]
    openpyxltools.replace(ws, to_replace="-3", value=98)
    assert_excel_worksheet_equal(ws, expected_ws)

    # wb.save(current_dir / "result.xlsx")
