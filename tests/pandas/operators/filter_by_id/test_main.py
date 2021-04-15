from pathlib import Path

import pytest

from macpie.pandas import file_to_dataframe

current_dir = Path("tests/pandas/operators/filter_by_id/").resolve()


def test_filter_by_id():

    df = file_to_dataframe(current_dir / "basic.xlsx")
    # ids list with invalid integer should raise ValueError
    ids = [1, 2, 'hello']
    with pytest.raises(ValueError):
        df.mac.filter_by_id('pidn', ids)

    # number of rows of filtered result should match number of ids
    ids = [2, 3, '4']
    result = df.mac.filter_by_id('pidn', ids)
    # result.to_excel(Path("tests/pandas/operators/filter_by_id/result.xlsx"), index=False)

    assert result.mac.num_rows() == 4
