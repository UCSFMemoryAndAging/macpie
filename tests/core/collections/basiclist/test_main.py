import macpie as mp


def test_basiclist(tmp_path):
    dset1 = mp.Dataset({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})

    dset1.to_excel(tmp_path / "dset1.xlsx")

    with mp.MACPieExcelFile(tmp_path / "dset1.xlsx") as reader:
        dset1_from_file = mp.read_excel(reader, sheet_name="NO_NAME")
    # dset1_from_file = mp.read_excel(tmp_path / "dset1.xlsx", sheet_name="NO_NAME")

    assert dset1.equals(dset1_from_file)

    dset2 = mp.Dataset(
        {"A": [1, 2, 3], "albert": [4, 5, 6], "C": [7, 8, 9]},
        id_col_name="albert",
        name="renee",
        tags=["a", "b"],
    )

    basic_list = mp.BasicList([dset1, dset2])

    with mp.MACPieExcelWriter(tmp_path / "basic_list.xlsx") as writer:
        basic_list.to_excel(writer)

    with mp.MACPieExcelFile(tmp_path / "basic_list.xlsx") as reader:
        basic_list_from_file = mp.read_excel(reader, as_collection=True)
    # basic_list_from_file = mp.read_excel(tmp_path / "basic_list.xlsx", as_collection=True)

    assert len(basic_list_from_file) == 2

    assert basic_list_from_file[0].equals(dset1)

    assert basic_list_from_file[1].equals(dset2)
