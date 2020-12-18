from datetime import datetime
from pathlib import Path

import openpyxl as pyxl
import pandas as pd

from macpie import util
from macpie.core import Datasheet, Databook


current_dir = Path("tests/core/datasheet/").resolve()

# output_dir = current_dir
output_dir = None


def test_datasheet():

    d = {
        'PIDN': [2, 2, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'InstrID': [7, 8, 9]
    }

    # multiindex for both col headers and row index
    df1 = pd.DataFrame(data=d)
    df1.columns = pd.MultiIndex.from_product([['CDR'], df1.columns])
    arrays = [['bar', 'br', 'baz'], [1, 2, 3]]
    df1.index = pd.MultiIndex.from_tuples(list(zip(*arrays)))
    ds1 = Datasheet('ds1', df1, display_index=True, display_header=True)

    # multiindex for just col headers
    df2 = pd.DataFrame(data=d)
    df2.columns = pd.MultiIndex.from_product([['FAQ'], df2.columns])
    ds2 = Datasheet('ds2', df2, display_index=True, display_header=True)

    # no multiindex, just a typical dataobject, but display index
    df3 = pd.DataFrame(data=d)
    ds3 = Datasheet('ds3', df3, display_index=True, display_header=True)

    # no multiindex, just a typical dataobject, and don't display index
    df4 = pd.DataFrame(data=d)
    ds4 = Datasheet('ds4', df4, display_index=False, display_header=True)

    # no multiindex, just a typical dataobject, and don't display index or header
    df5 = pd.DataFrame(data=d)
    ds5 = Datasheet('ds5', df5, display_index=False, display_header=False)

    results_path = current_dir / "results.xlsx"

    db = Databook()
    db.add_sheet(ds1)
    db.add_sheet(ds2)
    db.add_sheet(ds3)
    db.add_sheet(ds4)
    db.add_sheet(ds5)
    db.to_excel(results_path)

    results = pyxl.load_workbook(results_path)
    expected_results = pyxl.load_workbook(current_dir / "expected_results.xlsx")

    util.testing.assert_excels_equal(results, expected_results)

    results_path.unlink()
