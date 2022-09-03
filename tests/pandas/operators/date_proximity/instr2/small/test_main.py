from pathlib import Path

import pandas as pd

DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path(__file__).parent.absolute()


def test_instr2_small():

    dfs_dict = pd.read_excel(
        THIS_DIR / "instr2_small.xlsx", sheet_name=["primary", "expected_results"]
    )

    primary = dfs_dict["primary"]
    secondary_instr1 = pd.read_csv(DATA_DIR / "instr1_all.csv", parse_dates=[1])

    # test closest; earlier_or_later; 90 days
    small_result = primary.mac.date_proximity(
        secondary_instr1,
        id_on="pidn",
        date_on="dcdate",
        get="closest",
        when="earlier_or_later",
        days=90,
        left_link_id="instrid",
    )

    small_expected_result = dfs_dict["expected_results"]
    (left, right) = small_result.mac.conform(small_expected_result, dtypes=True)
    pd.testing.assert_frame_equal(left, right)
