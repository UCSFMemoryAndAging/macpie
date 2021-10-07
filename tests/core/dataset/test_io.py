from pathlib import Path

import numpy as np
import pandas as pd

from macpie.core.dataset import Dataset


current_dir = Path("tests/core/dataset/").resolve()


def test_io():
    d = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "date_bad": ["bad_date", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
        "id_col_name": [1, 2, 3],
        "id_col_with_dups": [1, 1, 3],
        "id_col_with_nan": [np.nan, np.nan, 3],
        "id_col_with_none": [None, None, 3],
    }

    dset = Dataset(
        data=d,
        id_col_name="id_col_name",
        date_col_name="date",
        id2_col_name="col3",
        name="test_name",
    )

    assert dset.name == "test_name"
