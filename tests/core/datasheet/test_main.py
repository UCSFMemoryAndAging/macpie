from datetime import datetime
from pathlib import Path

import pandas as pd

from macpie.core import Datasheet, Databook


current_dir = Path("tests/core/datasheet/")

# output_dir = current_dir
output_dir = None


def test():

    arrays = [['bar', 'br', 'baz'],
              [1, 2, 3]]

    tuples = list(zip(*arrays))

    row_index = pd.MultiIndex.from_tuples(tuples)

    d1 = {
        'PIDN': [2, 2, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'InstrID': [7, 8, 9]
    }
    df1 = pd.DataFrame(data=d1)
    df1.columns = pd.MultiIndex.from_product([['CDR'], df1.columns])

    df1.index = row_index

    ds = Datasheet('datasheet1', df1, display_index=True, display_header=True)

    # ds.to_excel(current_dir / "test.xlsx")
    ds2 = Datasheet('datasheet2', df1, display_index=True, display_header=True)
    db = Databook()
    db.add_sheet(ds)
    db.add_sheet(ds2)
    db.to_excel(current_dir / "testwb.xlsx")
