import filecmp
import shutil

from pathlib import Path
from click.testing import CliRunner
import pytest

import macpie as mp
from macpie.cli.macpie.main import main
from macpie.testing import assert_excels_equal, DebugDir


THIS_DIR = Path(__file__).parent.absolute()

RANDOM_SEED = 567


@pytest.mark.parametrize("filename", ["data.csv", "data.xlsx"])
def test_masker(tmp_path, filename, debugdir):
    # macpie masker --random-seed 567 --id-range 1 5 --id-cols pidn --date-cols dcdate --id2-range 11 15 --id2-cols instrid data.csv

    runner = CliRunner()

    cli_args = [
        "masker",
        "--random-seed",
        str(RANDOM_SEED),
        "--id-range",
        "1",
        "5",
        "--id-cols",
        "pidn",
        "--date-cols",
        "dcdate",
        "--id2-range",
        "11",
        "15",
        "--id2-cols",
        "instrid",
        str(Path(THIS_DIR / filename).resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, cli_args)
        assert result.exit_code == 0
        # get the results file
        results_path = next(Path(".").rglob(filename)).resolve()
        expected_results_path = Path(THIS_DIR / ("expected_result" + results_path.suffix))

        if results_path.suffix == ".xlsx":
            assert_excels_equal(results_path, expected_results_path)
        elif results_path.suffix == ".csv":
            assert filecmp.cmp(results_path, expected_results_path, shallow=False) is True

        # copy file to current dir if you want to debug more
        if debugdir:
            with DebugDir(debugdir):
                expected_resultpath = mp.shelltools.copy_file_same_dir(
                    results_path, new_file_name="expected_" + filename
                )
                shutil.move(expected_resultpath, debugdir)

    return results_path
