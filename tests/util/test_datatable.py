import pandas as pd

from macpie.util import DataTable


def test_datatable():
    l1 = [1, 2]
    l2 = [3, 4, 5]
    l3 = (6,)

    dt = DataTable([l1, l2])
    assert dt.data == [[1, 2, None], [3, 4, 5]]

    dt = DataTable([l1, l2], axis=1)
    assert dt.data == [[1, 3], [2, 4], [None, 5]]

    dt = DataTable.from_seqs(l1, l2, l3, axis=0)
    assert dt.data == [[1, 2, None], [3, 4, 5], [6, None, None]]

    dt = DataTable.from_seqs(l1, l2, l3, axis=1)
    assert dt.data == [[1, 3, 6], [2, 4, None], [None, 5, None]]

    df = pd.DataFrame({"col1": [1, 2], "col2": ["3", None]})
    dt = DataTable.from_df(df)
    assert dt.data == [[1, "3"], [2, None]]

    dt = DataTable([l1, l2])
    dt.transpose()
    assert dt.data == [[1, 3], [2, 4], [None, 5]]
