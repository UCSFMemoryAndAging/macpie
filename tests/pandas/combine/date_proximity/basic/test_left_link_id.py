from pathlib import Path

import pandas as pd

from macpie.pandas import read_file


THIS_DIR = Path(__file__).parent.absolute()


primary = read_file(THIS_DIR / "primary_no_dupes.xlsx")

secondary = read_file(THIS_DIR / "secondary.xlsx")


def test_left_link_id_blank_merge_partial():
    # partial merge

    result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        merge="partial",
    )

    expected_result = read_file(THIS_DIR / "left_link_id_blank_merge_partial_expected_result.xlsx")
    (left, right) = result.mac.conform(expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)


def test_left_link_id_blank_merge_full():
    # full merge

    result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        merge="full",
    )

    expected_result = read_file(THIS_DIR / "left_link_id_blank_merge_full_expected_result.xlsx")
    (left, right) = result.mac.conform(expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)
