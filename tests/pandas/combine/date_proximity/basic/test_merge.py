from pathlib import Path

import pandas as pd

from macpie.pandas import read_file


THIS_DIR = Path(__file__).parent.absolute()

primary = read_file(THIS_DIR / "primary.xlsx")

secondary = read_file(THIS_DIR / "secondary.xlsx")


def test_merge_partial():
    # partial merge

    merge_partial_result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        merge="partial",
    )

    merge_partial_expected_result = read_file(THIS_DIR / "merge_partial_expected_result.xlsx")

    (left, right) = merge_partial_result.mac.conform(merge_partial_expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)

    # test that results are same when using equivalent id and date params
    test_id_on_params = primary.mac.date_proximity(
        secondary,
        id_left_on="pidn",
        id_right_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        merge="partial",
    )

    test_date_on_params = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_left_on="dcdate",
        date_right_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        merge="partial",
    )

    # test using id_left_on and id_right_on params
    assert merge_partial_result.equals(test_id_on_params)

    # test using date_left_on and date_right_on params
    assert merge_partial_result.equals(test_date_on_params)


def test_merge_full():
    # full merge

    merge_full_result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        merge="full",
    )

    merge_full_expected_result = read_file(THIS_DIR / "merge_full_expected_result.xlsx")

    (left, right) = merge_full_result.mac.conform(merge_full_expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)
