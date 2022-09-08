from pathlib import Path

import pandas as pd

from macpie.pandas import read_file


THIS_DIR = Path(__file__).parent.absolute()

primary = read_file(THIS_DIR / "small.xlsx")

dfs_dict = pd.read_excel(
    THIS_DIR / "small.xlsx", sheet_name=["small_anchor", "instr2_all_linked", "instr3_all_linked"]
)

small_anchor = dfs_dict["small_anchor"]
instr2_all_linked = dfs_dict["instr2_all_linked"]
instr3_all_linked = dfs_dict["instr3_all_linked"]


def test_add_suffixes_false():
    result = small_anchor.mac.merge(
        instr2_all_linked,
        left_on=["pidn", "dcdate", "instrid"],
        right_on=["pidn_x", "dcdate_x", "instrid_x"],
        merge_suffixes=("_a", "_b"),
        add_suffixes=False,
    ).mac.merge(
        instr3_all_linked,
        left_on=["pidn_a", "dcdate_a", "instrid_a"],
        right_on=["pidn_x", "dcdate_x", "instrid_x"],
        merge_suffixes=(None, "_c"),
        add_suffixes=False,
    )

    expected_result = pd.read_excel(THIS_DIR / "add_suffixes_false_expected_result.xlsx")

    pd.testing.assert_frame_equal(result, expected_result)


def test_add_suffixes_true():
    result = small_anchor.mac.merge(
        instr2_all_linked,
        left_on=["pidn", "dcdate", "instrid"],
        right_on=["pidn_x", "dcdate_x", "instrid_x"],
        merge_suffixes=("_a", "_b"),
        add_suffixes=True,
    ).mac.merge(
        instr3_all_linked,
        left_on=["pidn_a", "dcdate_a", "instrid_a"],
        right_on=["pidn_x", "dcdate_x", "instrid_x"],
        merge_suffixes=(None, "_c"),
        add_suffixes=True,
    )

    expected_result = pd.read_excel(THIS_DIR / "add_suffixes_true_expected_result.xlsx")

    pd.testing.assert_frame_equal(result, expected_result)


def test_with_index():
    result = small_anchor.mac.merge(
        instr2_all_linked,
        left_on=["pidn", "dcdate", "instrid"],
        right_on=["pidn_x", "dcdate_x", "instrid_x"],
        merge_suffixes=("_a", "_b"),
        add_suffixes=False,
        add_indexes=("small_anchor", "instr2_all_linked"),
    ).mac.merge(
        instr3_all_linked,
        left_on=[
            ("small_anchor", "pidn"),
            ("small_anchor", "dcdate"),
            ("small_anchor", "instrid"),
        ],
        right_on=["pidn_x", "dcdate_x", "instrid_x"],
        merge_suffixes=("_a", "_b"),
        add_suffixes=False,
        add_indexes=(None, "instr3_all_linked"),
    )

    expected_result = pd.read_excel(
        THIS_DIR / "with_index_expected_result.xlsx", index_col=0, header=[0, 1]
    )

    assert result.columns.equals(expected_result.columns)

    pd.testing.assert_frame_equal(result, expected_result)
