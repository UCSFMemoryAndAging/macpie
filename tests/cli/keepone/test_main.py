from pathlib import Path

from click.testing import CliRunner
import pytest

from macpie.cli.main import main


@pytest.mark.slow
def test_cli_keepone():
    # macpie -j pidn -d dcdate keepone -k earliest tests/data/instr1_primaryall.csv

    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'keepone',
        '--keep', 'earliest',
        str(Path("tests/data/instr1_primaryall.csv").resolve())
    ]

    with runner.isolated_filesystem():
        result = runner.invoke(main, cli_args)

        assert result.exit_code == 0
