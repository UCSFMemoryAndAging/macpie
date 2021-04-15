from pathlib import Path
from shutil import copy
from click.testing import CliRunner
import pytest

from macpie.cli.main import main


data_dir = Path("tests/data/").resolve()
current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None


@pytest.fixture(scope="session")
def cli_keepone_big(tmp_path_factory):
    # macpie -j pidn -d dcdate keepone -k earliest tests/data/instr1_primaryall.csv

    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'keepone',
        '--keep', 'earliest',
        str(Path(data_dir / "instr1_primaryall.csv").resolve())
    ]

    with runner.isolated_filesystem():
        result = runner.invoke(main, cli_args)
        assert result.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob('**/result*xlsx'))
        return Path(copy(results_path.resolve(),
                    tmp_path_factory.mktemp("keepone_big")))
