from pathlib import Path

import pandas as pd

from macpie._config import get_option
from macpie.pandas.io import read_file

THIS_DIR = Path("tests/pandas/operators/date_proximity/dupes/").resolve()


COL_FILTER_KWARGS = {
    "filter_kwargs": {
        "items": [
            get_option("column.system.abs_diff_days"),
            get_option("column.system.diff_days"),
            get_option("column.system.duplicates"),
            "_abs_diff_days",
            "_diff_days",
            "_duplicates",
        ],
        "invert": True,
    }
}


def test_dupes():

    primary = read_file(THIS_DIR / "primary.xlsx")
    secondary = read_file(THIS_DIR / "secondary.xlsx")

    dupes_result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        merge="full",
        duplicates_indicator=True,
    )

    dupes_expected_result = read_file(THIS_DIR / "dupes_expected_result.xlsx")

    (left, right) = dupes_result.mac.conform(
        dupes_expected_result, filter_kwargs=COL_FILTER_KWARGS, dtypes=True
    )
    pd.testing.assert_frame_equal(left, right)
