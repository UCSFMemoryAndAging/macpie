import macpie as mp


def test_display_name_generator():
    dset = mp.Dataset(
        {"A": [1, 2, 3], "albert": [4, 5, 6], "C": [7, 8, 9]},
        id_col_name="albert",
        name="renee",
        tags=["a", "b"],
    )

    dset.display_name == "renee_a_b"
    dset.display_name_generator = mp.MergeableAnchoredList.dataset_display_name_generator
    dset.display_name == "renee"


def test_read_file(cli_link_small_with_merge):
    mal = mp.read_excel(cli_link_small_with_merge, as_collection=True)

    assert type(mal) is mp.MergeableAnchoredList

    mal_dict = mal.to_excel_dict()

    assert mal_dict["primary"]["name"] == "small"
    assert mal_dict["primary"]["id_col_name"] == "InstrID"


def test_dups(cli_link_small_with_dups):
    mal = mp.read_excel(cli_link_small_with_dups, as_collection=True)

    dups = mal.get_duplicates()

    assert len(dups["instr2_all"]) == 12
    assert len(dups["instr3_all"]) == 17
