from pathlib import Path

import pandas as pd

from macpie import get_option
from macpie.pandas import read_file


DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path(__file__).parent.absolute()

COL_FILTER_KWARGS = {
    "items": ["PIDN_x", "VType", "DayDiff", "link_id"],
    "regex": "^" + get_option("column.system.prefix"),
    "invert": True,
}


dfs_dict = pd.read_excel(
    DATA_DIR / "instr1.xlsx",
    sheet_name=[
        "primary",
        "closest_earlier_or_later_90",
        "closest_later_90",
        "closest_earlier_90",
        "all_earlier_or_later_90",
        "all_later_90",
        "all_earlier_90",
    ],
)

primary = dfs_dict["primary"]
secondary = read_file(DATA_DIR / "instr1_all.csv")


def test_instr1_closest_earlier_or_later_90():

    # test closest; earlier_or_later; 90 days
    closest_earlier_or_later_90_result = primary.mac.date_proximity(
        secondary, id_on="pidn", date_on="dcdate", get="closest", when="earlier_or_later", days=90
    )

    closest_earlier_or_later_90_expected_result = dfs_dict["closest_earlier_or_later_90"]

    (left, right) = closest_earlier_or_later_90_result.mac.conform(
        closest_earlier_or_later_90_expected_result,
        subset_pair_kwargs=COL_FILTER_KWARGS,
        dtypes=True,
        index_order=True,
    )
    pd.testing.assert_frame_equal(left, right)


def test_instr1_closest_later_90():

    # test closest; later; 90 days
    closest_later_90_result = primary.mac.date_proximity(
        secondary, id_on="pidn", date_on="dcdate", get="closest", when="later", days=90
    )

    closest_later_90_expected_result = dfs_dict["closest_later_90"]

    (left, right) = closest_later_90_result.mac.conform(
        closest_later_90_expected_result,
        subset_pair_kwargs=COL_FILTER_KWARGS,
        dtypes=True,
        index_order=True,
    )
    pd.testing.assert_frame_equal(left, right)


def test_instr1_closest_earlier_90():
    # test closest; earlier; 90 days
    closest_earlier_90_result = primary.mac.date_proximity(
        secondary, id_on="pidn", date_on="dcdate", get="closest", when="earlier", days=90
    )

    closest_earlier_90_expected_result = dfs_dict["closest_earlier_90"]

    (left, right) = closest_earlier_90_result.mac.conform(
        closest_earlier_90_expected_result,
        subset_pair_kwargs=COL_FILTER_KWARGS,
        dtypes=True,
        index_order=True,
    )
    pd.testing.assert_frame_equal(left, right)


def test_instr1_all_earlier_or_later_90():

    # test all; earlier_or_later; 90 days
    all_earlier_or_later_90_result = primary.mac.date_proximity(
        secondary, id_on="pidn", date_on="dcdate", get="all", when="earlier_or_later", days=90
    )

    all_earlier_or_later_90_expected_result = dfs_dict["all_earlier_or_later_90"]

    (left, right) = all_earlier_or_later_90_result.mac.conform(
        all_earlier_or_later_90_expected_result,
        subset_pair_kwargs=COL_FILTER_KWARGS,
        dtypes=True,
        index_order=True,
        values_order=True,
    )
    pd.testing.assert_frame_equal(left, right)


def test_instr1_all_later_90():
    # test all; later; 90 days
    all_later_90_result = primary.mac.date_proximity(
        secondary, id_on="pidn", date_on="dcdate", get="all", when="later", days=90
    )

    all_later_90_expected_result = dfs_dict["all_later_90"]

    (left, right) = all_later_90_result.mac.conform(
        all_later_90_expected_result,
        subset_pair_kwargs=COL_FILTER_KWARGS,
        dtypes=True,
        index_order=True,
        values_order=True,
    )
    pd.testing.assert_frame_equal(left, right)


def test_instr1_all_earlier_90():
    # test all; earlier; 90 days
    all_earlier_90_result = primary.mac.date_proximity(
        secondary, id_on="pidn", date_on="dcdate", get="all", when="earlier", days=90
    )

    all_earlier_90_expected_result = dfs_dict["all_earlier_90"]

    (left, right) = all_earlier_90_result.mac.conform(
        all_earlier_90_expected_result,
        subset_pair_kwargs=COL_FILTER_KWARGS,
        dtypes=True,
        index_order=True,
        values_order=True,
    )
    pd.testing.assert_frame_equal(left, right)
