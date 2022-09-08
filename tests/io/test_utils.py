from pathlib import Path

import macpie.io.utils as utils


DATA_DIR = Path("tests/io/data/").resolve()


def test_detect_format():
    assert utils.detect_format(DATA_DIR / "empty.csv") is None
    assert utils.detect_format(DATA_DIR / "test.csv") == "csv"
    assert utils.detect_format(DATA_DIR / "tab_delimited.csv") == "tsv"
    assert utils.detect_format(DATA_DIR / "bad_xl.xlsx") is None
    assert utils.detect_format(DATA_DIR / "test.xlsx") == "xlsx"
