from pathlib import Path
import macpie as mp
import pandas as pd

data_dir = Path("tests/data/").resolve()


d = Path("/Users/alee7/ucsf/git/macpie/tests/core/dataset/")
primary = mp.LavaDataset.from_file(d / "primary.xlsx")
secondary = mp.LavaDataset.from_file(d / "secondary.xlsx")

a = pd.concat([primary], keys=["Foo1"], axis="columns")
b = pd.concat([a], keys=["Foo2"], axis="columns")
c = primary.date_proximity(secondary, get="closest", when="earlier_or_later", days=90)

primary.group_by_keep_one()

assert len(primary.history) == 2

record1 = primary.history[0]
assert record1["method_name"] == "date_proximity"

record2 = primary.history[1]
assert record2["method_name"] == "group_by_keep_one"
