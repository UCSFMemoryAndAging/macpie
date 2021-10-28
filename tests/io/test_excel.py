from pathlib import Path

import macpie as mp
import pandas as pd


current_dir = Path(__file__).parent.absolute()


data = [
    [1, 4, 7, "1/1/2001", 1, "1/2/2001"],
    [2, 5, 8, "2/2/2002", 2, "2/3/2003"],
    [3, 6, 9, "3/3/2003", 3, "3/4/2003"],
]

columns = ["col1", "col2", "col3", "date", "ids", "date2"]

mi_columns = pd.MultiIndex.from_product([["level"], columns])

df = pd.DataFrame(data, columns=columns)

dset = mp.Dataset(df, id_col_name="ids", date_col_name="date")

mi_df = pd.DataFrame(data=data, columns=mi_columns)

mi_dset = mp.Dataset(
    mi_df, id_col_name=("level", "ids"), date_col_name=("level", "date"), name="mi_test_name"
)

basic_list = mp.BasicList([dset, mi_dset])


def test_single_dataset(tmp_path):

    dset.to_excel(tmp_path / "dset.xlsx")

    dset_from_file = mp.read_excel(tmp_path / "dset.xlsx")

    assert dset.equals(dset_from_file)

    mi_dset.to_excel(tmp_path / "mi_dset.xlsx")

    mi_dset_from_file = mp.read_excel(tmp_path / "mi_dset.xlsx")

    assert mi_dset.equals(mi_dset_from_file)


def test_multiple_datasets(tmp_path):

    with mp.MACPieExcelWriter(tmp_path / "basic_list.xlsx") as writer:
        basic_list.to_excel(writer)

    basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx")

    assert dset.equals(basic_list_from_file)

    basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name=0)

    assert dset.equals(basic_list_from_file)

    basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name="mi_test_name")

    assert mi_dset.equals(basic_list_from_file)

    basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name=[0, 1])

    assert dset.equals(basic_list_from_file[0])

    assert mi_dset.equals(basic_list_from_file[1])

    basic_list_from_file = mp.read_excel(
        tmp_path / "basic_list.xlsx", sheet_name=[0, "mi_test_name"]
    )

    assert dset.equals(basic_list_from_file[0])

    assert mi_dset.equals(basic_list_from_file["mi_test_name"])

    basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", sheet_name=None)

    assert dset.equals(basic_list_from_file["NO_NAME"])

    assert mi_dset.equals(basic_list_from_file["mi_test_name"])
