from pathlib import Path

import pandas as pd

import macpie as mp


DATA_DIR = Path("tests/core/dataset/")


def test():
    primary = mp.LavaDataset.from_file(DATA_DIR / "primary.xlsx")
    secondary = mp.LavaDataset.from_file(DATA_DIR / "secondary.xlsx")

    a = pd.concat([primary], keys=["Foo1"], axis="columns")
    b = pd.concat([a], keys=["Foo2"], axis="columns")
    c = primary.date_proximity(secondary, get="closest", when="earlier_or_later", days=90)

    primary.group_by_keep_one()

    assert len(primary.history) == 2

    record1 = primary.history[0]
    assert record1["method_name"] == "date_proximity"

    record2 = primary.history[1]
    assert record2["method_name"] == "group_by_keep_one"
