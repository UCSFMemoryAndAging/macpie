from pathlib import Path

import macpie as mp


THIS_DIR = Path(__file__).parent.absolute()


def test_history():
    primary = mp.LavaDataset.from_file(THIS_DIR / "primary.xlsx")
    secondary = mp.LavaDataset.from_file(THIS_DIR / "secondary.xlsx")

    secondary.date_proximity(primary, get="closest", when="earlier_or_later", days=90)

    secondary.group_by_keep_one()

    assert len(secondary.history) == 2

    record1 = secondary.history[0]
    assert record1["method_name"] == "date_proximity"

    record2 = secondary.history[1]
    assert record2["method_name"] == "group_by_keep_one"
