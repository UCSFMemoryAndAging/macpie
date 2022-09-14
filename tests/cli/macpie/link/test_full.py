from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd
import pytest

import macpie as mp
from macpie.cli.macpie.main import main
from macpie.testing import DebugDir

DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path(__file__).parent.absolute()

COL_FILTER_KWARGS = {
    "items": ["PIDN", "VType", "InstrID_x", "link_id_x"],
    "regex": "^" + mp.get_option("column.system.prefix"),
    "invert": True,
}

expected_dict = pd.read_excel(
    THIS_DIR / "full.xlsx", sheet_name=["LINK_INSTR1", "INSTR2_linked", "INSTR3_linked"]
)

expected_primary = expected_dict["LINK_INSTR1"]
expected_secondary_instr2 = expected_dict["INSTR2_linked"]
expected_secondary_instr3 = expected_dict["INSTR3_linked"]


@pytest.mark.slow
def test_full_no_merge(cli_link_full_no_merge, debugdir):
    # copy file to current dir if you want to debug more
    if debugdir:
        with DebugDir(debugdir):
            copy(cli_link_full_no_merge, debugdir)

    results_dict = pd.read_excel(
        cli_link_full_no_merge,
        sheet_name=["full_anchor", "instr2_all_DUPS", "instr3_all_DUPS"],
    )

    result_primary = results_dict["full_anchor"]
    result_secondary_instr2 = results_dict["instr2_all_DUPS"]
    result_secondary_instr3 = results_dict["instr3_all_DUPS"]

    (left, right) = result_primary.mac.conform(expected_primary, values_order=True)
    pd.testing.assert_frame_equal(left, right)

    (left, right) = result_secondary_instr2.mac.conform(
        expected_secondary_instr2, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)

    (left, right) = result_secondary_instr3.mac.conform(
        expected_secondary_instr3, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)


@pytest.mark.slow
def test_full_no_link_id(tmp_path, debugdir):
    # macpie link -g closest tests/cli/macpie/link/full_no_link_id.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv

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
        str((THIS_DIR / "full_no_link_id.xlsx").resolve()),
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

        results_dict = pd.read_excel(
            results_path, sheet_name=["instr2_all_DUPS", "instr3_all_DUPS"]
        )

        result_secondary_instr2 = results_dict["instr2_all_DUPS"]
        result_secondary_instr3 = results_dict["instr3_all_DUPS"]

        (left, right) = result_secondary_instr2.mac.conform(
            expected_secondary_instr2, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
        )
        pd.testing.assert_frame_equal(left, right)

        (left, right) = result_secondary_instr3.mac.conform(
            expected_secondary_instr3, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
        )
        pd.testing.assert_frame_equal(left, right)
