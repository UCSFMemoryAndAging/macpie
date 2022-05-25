import pandas as pd

from macpie.util import TableList


def test_tablelist():
    l1 = [1, 2]
    l2 = [3, 4, 5]
    l3 = (6,)

    tlist = TableList([l1, l2])
    assert tlist.data == [[1, 2, None], [3, 4, 5]]

    tlist = TableList([l1, l2], axis=1)
    assert tlist.data == [[1, 3], [2, 4], [None, 5]]

    tlist = TableList.from_seqs(l1, l2, l3, axis=0)
    assert tlist.data == [[1, 2, None], [3, 4, 5], [6, None, None]]

    tlist = TableList.from_seqs(l1, l2, l3, axis=1)
    assert tlist.data == [[1, 3, 6], [2, 4, None], [None, 5, None]]

    df = pd.DataFrame({"col1": [1, 2], "col2": ["3", None]})
    tlist = TableList.from_df(df)
    assert tlist.data == [[1, "3"], [2, None]]
