from pathlib import Path

import pandas as pd

import macpie as mp
from macpie.pandas import read_file

THIS_DIR = Path(__file__).parent.absolute()


COL_FILTER_KWARGS = {
    "items": [
        mp.get_option("column.system.abs_diff_days"),
        mp.get_option("column.system.diff_days"),
        mp.get_option("column.system.duplicates"),
        "_abs_diff_days",
        "_diff_days",
        "_duplicates",
    ],
    "invert": True,
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
        dupes_expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, dtypes=True
    )
    pd.testing.assert_frame_equal(left, right)
