from pathlib import Path

import pandas as pd

from macpie.pandas import read_file


THIS_DIR = Path(__file__).parent.absolute()


primary = read_file(THIS_DIR / "primary_no_dupes.xlsx")

secondary = read_file(THIS_DIR / "secondary.xlsx")


def test_dropna_true():

    result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        dropna=True,
        merge="partial",
    ).reset_index(drop=True)

    expected_result = read_file(THIS_DIR / "dropna_true_expected_result.xlsx")
    (left, right) = result.mac.conform(expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right, check_categorical=True)


def test_dropna_true_merge_full():

    result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        dropna=True,
        merge="full",
    ).reset_index(drop=True)

    expected_result = read_file(THIS_DIR / "dropna_true_merge_full_expected_result.xlsx")
    (left, right) = result.mac.conform(expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)


def test_dropna_false():

    result = primary.mac.date_proximity(
        secondary,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        dropna=False,
        merge="partial",
    )

    expected_result = read_file(THIS_DIR / "dropna_false_expected_result.xlsx")
    (left, right) = result.mac.conform(expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)
