from pathlib import Path

from click.testing import CliRunner
import pytest

from macpie.cli.macpie.main import main


DATA_DIR = Path("tests/data/").resolve()


@pytest.fixture(scope="session")
def cli_keepone_big(tmp_path_factory):
    # macpie -j pidn -d dcdate keepone -k earliest tests/data/instr1_primaryall.csv

    runner = CliRunner()

    cli_args = [
        "--id2-col",
        "pidn",
        "--date-col",
        "dcdate",
        "keepone",
        "--keep",
        "earliest",
        str(Path(DATA_DIR / "instr1_primaryall.csv").resolve()),
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path_factory.mktemp("keepone_big")):
        result = runner.invoke(main, cli_args)
        assert result.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob("**/*.xlsx")).resolve()

    return results_path
