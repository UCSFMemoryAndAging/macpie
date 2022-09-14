from pathlib import Path

import pandas as pd
import pytest

from macpie._config import get_option
from macpie.pandas.io import read_file


DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path(__file__).parent.absolute()

COL_FILTER_KWARGS = {
    "items": ["PIDN", "VType", "DayDiff"],
    "regex": "^" + get_option("column.system.prefix"),
    "invert": True,
}


dfs_dict = pd.read_excel(
    DATA_DIR / "instr2.xlsx", sheet_name=["LINK_INSTR2", "INSTR1_linked", "INSTR3_linked"]
)

primary = dfs_dict["LINK_INSTR2"]


@pytest.mark.slow
def test_secondary_instr1():

    secondary_instr1 = read_file(DATA_DIR / "instr1_all.csv")

    # test closest; earlier_or_later; 90 days
    instr1_result = primary.mac.date_proximity(
        secondary_instr1,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        duplicates_indicator=True,
    )

    instr1_expected_result = dfs_dict["INSTR1_linked"]

    (left, right) = instr1_result.mac.conform(
        instr1_expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)


@pytest.mark.slow
def test_secondary_instr3():

    secondary_instr3 = read_file(DATA_DIR / "instr3_all.csv")

    # test closest; earlier_or_later; 90 days
    instr3_result = primary.mac.date_proximity(
        secondary_instr3,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
        duplicates_indicator=True,
    )

    instr3_expected_result = dfs_dict["INSTR3_linked"]

    (left, right) = instr3_result.mac.conform(
        instr3_expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)
