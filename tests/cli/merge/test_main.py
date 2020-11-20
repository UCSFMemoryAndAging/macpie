from pathlib import Path

current_dir = Path("tests/cli/merge/").resolve()


def test_small_no_merge():
    p = current_dir / "small_no_merge.xlsx"
