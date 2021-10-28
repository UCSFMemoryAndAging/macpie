from pathlib import Path
from shutil import copy
from click.testing import CliRunner
import pytest

from macpie.cli.macpie.main import main

data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/cli/macpie/link/").resolve()

# output_dir = current_dir
output_dir = None


@pytest.fixture(scope="session")
def cli_link_small_with_merge(tmp_path_factory):
    # macpie link -g closest tests/cli/macpie/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv

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
        str((current_dir / "small.xlsx").resolve()),
        str((data_dir / "instr2_all.csv").resolve()),
        str((data_dir / "instr3_all.csv").resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path_factory.mktemp("cli_link_small_with_merge")):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob("**/result*xlsx")).resolve()

    return results_path


@pytest.fixture(scope="session")
def cli_link_small_no_merge(tmp_path_factory):
    # macpie link -g closest --no-merge-results tests/cli/macpie/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv  # noqa: E501

    runner = CliRunner()

    cli_args = [
        "--id2-col",
        "pidn",
        "--date-col",
        "dcdate",
        "link",
        "--no-merge-results",
        "--primary-keep",
        "all",
        "--secondary-get",
        "closest",
        "--secondary-days",
        90,
        "--secondary-when",
        "earlier_or_later",
        str((current_dir / "small.xlsx").resolve()),
        str((data_dir / "instr2_all.csv").resolve()),
        str((data_dir / "instr3_all.csv").resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path_factory.mktemp("cli_link_small_no_merge")):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob("**/result*xlsx")).resolve()

    return results_path


@pytest.fixture(scope="session")
def cli_link_full_no_merge(tmp_path_factory):
    # macpie link -g closest --no-merge-results tests/cli/macpie/link/full.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv  # noqa: E501

    runner = CliRunner()

    cli_args = [
        "--id2-col",
        "pidn",
        "--date-col",
        "dcdate",
        "link",
        "--no-merge-results",
        "--primary-keep",
        "all",
        "--secondary-get",
        "closest",
        "--secondary-days",
        90,
        "--secondary-when",
        "earlier_or_later",
        str((current_dir / "full.xlsx").resolve()),
        str((data_dir / "instr2_all.csv").resolve()),
        str((data_dir / "instr3_all.csv").resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path_factory.mktemp("cli_link_full_no_merge")):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob("**/result*xlsx")).resolve()

    return results_path


@pytest.fixture(scope="session")
def cli_link_small_with_dups(tmp_path_factory):
    # macpie link -g closest tests/cli/macpie/link/small_with_dups.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv

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
        str((current_dir / "small_with_dups.xlsx").resolve()),
        str((data_dir / "instr2_all.csv").resolve()),
        str((data_dir / "instr3_all.csv").resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path_factory.mktemp("cli_link_small_with_dups")):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob("**/result*xlsx")).resolve()

    return results_path
