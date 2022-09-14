from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd

import macpie as mp
from macpie.cli.macpie.main import main
from macpie.testing import DebugDir

THIS_DIR = Path(__file__).parent.absolute()

DATA_DIR = Path("tests/data/").resolve()

COL_FILTER_KWARGS = {
    "regex": "^" + mp.get_option("column.system.prefix"),
    "invert": True,
}


def test_small_with_merge(cli_link_small_with_merge, debugdir):
    expected = pd.read_excel(
        THIS_DIR / "small_with_merge_expected_result.xlsx",
        sheet_name=mp.MergeableAnchoredList.merged_dsetname,
        index_col=None,
        header=[0, 1],
    )

    # copy file to current dir if you want to debug more
    if debugdir:
        with DebugDir(debugdir):
            copy(cli_link_small_with_merge, debugdir)

    result = pd.read_excel(
        cli_link_small_with_merge,
        sheet_name=mp.MergeableAnchoredList.merged_dsetname,
        index_col=None,
        header=[0, 1],
    )

    (left, right) = result.mac.conform(
        expected, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)


def test_small_no_merge(cli_link_small_no_merge, debugdir):
    expected_dict = pd.read_excel(
        THIS_DIR / "small.xlsx", sheet_name=["LINK_INSTR1", "INSTR2_linked", "INSTR3_linked"]
    )

    expected_primary = expected_dict["LINK_INSTR1"]
    expected_secondary_instr2 = expected_dict["INSTR2_linked"]
    expected_secondary_instr3 = expected_dict["INSTR3_linked"]

    # copy file to current dir if you want to debug more
    if debugdir:
        with DebugDir(debugdir):
            copy(cli_link_small_no_merge, debugdir)

    results_dict = pd.read_excel(
        cli_link_small_no_merge,
        sheet_name=["small_anchor", "instr2_all_linked", "instr3_all_linked"],
    )

    result_primary = results_dict["small_anchor"]
    result_secondary_instr2 = results_dict["instr2_all_linked"]
    result_secondary_instr3 = results_dict["instr3_all_linked"]

    (left, right) = result_primary.mac.conform(
        expected_primary, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)

    COL_FILTER_KWARGS["items"] = [
        mp.get_option("column.system.abs_diff_days"),
        mp.get_option("column.system.diff_days"),
        "PIDN",
        "VType",
        "_merge",
    ]

    (left, right) = result_secondary_instr2.mac.conform(
        expected_secondary_instr2, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)

    (left, right) = result_secondary_instr3.mac.conform(
        expected_secondary_instr3, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)

    del COL_FILTER_KWARGS["items"]


def test_small_no_link_id(tmp_path, debugdir):
    # macpie link -g closest tests/cli/macpie/link/small_no_link_id.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv  # noqa: E501

    expected_result = pd.read_excel(
        THIS_DIR / "small_no_link_id_expected_result.xlsx",
        sheet_name=mp.MergeableAnchoredList.merged_dsetname,
        index_col=None,
        header=[0, 1],
    )

    runner = CliRunner()

    cli_args = [
        "--id2-col",
        "pidn",
        "--date-col",
        "dcdate",
        "link",
        "--primary-keep",
        "all",
        "--secondary-get",
        "closest",
        "--secondary-days",
        90,
        "--secondary-when",
        "earlier_or_later",
        str((THIS_DIR / "small_no_link_id.xlsx").resolve()),
        str((DATA_DIR / "instr2_all.csv").resolve()),
        str((DATA_DIR / "instr3_all.csv").resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)

        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob("**/*.xlsx"))

        # copy file to current dir if you want to debug more
        if debugdir:
            with DebugDir(debugdir):
                copy(results_path, debugdir)

        results = pd.read_excel(
            results_path,
            sheet_name=mp.MergeableAnchoredList.merged_dsetname,
            index_col=None,
            header=[0, 1],
        )

        (left, right) = results.mac.conform(
            expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
        )
        pd.testing.assert_frame_equal(left, right)


def test_small_link_suffixes(tmp_path, debugdir):
    # macpie link -g closest tests/cli/macpie/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv  # noqa: E501

    runner = CliRunner()

    cli_args = [
        "--id2-col",
        "pidn",
        "--date-col",
        "dcdate",
        "link",
        "--primary-keep",
        "all",
        "--secondary-get",
        "closest",
        "--secondary-days",
        90,
        "--secondary-when",
        "earlier_or_later",
        str((THIS_DIR / "small.xlsx").resolve()),
        str((DATA_DIR / "instr2_all.csv").resolve()),
        str((DATA_DIR / "instr3_all.csv").resolve()),
    ]

    mp.set_option("operators.binary.column_suffixes", ("_link", "_y"))

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob("**/*.xlsx")).resolve()

        expected_result = pd.read_excel(
            THIS_DIR / "small_link_suffixes_expected_result.xlsx",
            sheet_name=mp.MergeableAnchoredList.merged_dsetname,
            index_col=None,
            header=[0, 1],
        )

        # copy file to current dir if you want to debug more
        if debugdir:
            with DebugDir(debugdir):
                copy(results_path, debugdir)

        results = pd.read_excel(
            results_path,
            sheet_name=mp.MergeableAnchoredList.merged_dsetname,
            index_col=None,
            header=[0, 1],
        )

        (left, right) = results.mac.conform(
            expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
        )
        pd.testing.assert_frame_equal(left, right)

    mp.reset_option("operators.binary.column_suffixes")
