from pathlib import Path

from click.testing import CliRunner

from macpie.cli.macpie.main import main

current_dir = Path("tests/cli/macpie/data/").resolve()


def test_basic(tmp_path):
    runner = CliRunner()

    temp_file = "link " + str((current_dir / "~$test.csv").resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, temp_file, catch_exceptions=False)
        assert result.exit_code != 0

    results_file = "link " + str((current_dir / "results_test.csv").resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, results_file)
        assert result.exit_code != 0

    bad_suffix = "link " + str((current_dir / "test.zzz").resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, bad_suffix)
        assert result.exit_code != 0

    file_no_exist = "link " + str((current_dir / "not_exists.xlsx").resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, file_no_exist)
        assert result.exit_code != 0

    primary_is_dir = "link " + str(current_dir.resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, primary_is_dir)
        assert result.exit_code != 0

    bad_extension = "link " + str((current_dir / "badfile.pdf").resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, bad_extension)
        assert result.exit_code != 0

    file_no_exist = "link " + str((current_dir / "not_exists.xlsx").resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, file_no_exist)
        assert result.exit_code != 0

    primary_is_dir = "link " + str(current_dir.resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, primary_is_dir)
        assert result.exit_code != 0

    validate_paths = "keepone " + str((current_dir).resolve())
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, validate_paths)
        assert result.exit_code != 0
