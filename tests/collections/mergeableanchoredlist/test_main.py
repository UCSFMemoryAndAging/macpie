from pathlib import Path

import macpie as mp
from macpie.collections.mergeableanchoredlist import MergeableAnchoredList


current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None


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
    mal = MergeableAnchoredList.from_excel(cli_link_small_with_merge)

    mal_dict = mal.to_dict()

    assert mal_dict["primary"].name == "small"
    assert mal_dict["primary"].id_col_name == "InstrID"

    mal_info = mal.get_collection_info().to_dict()

    assert mal_info["class_name"] == "MergeableAnchoredList"
    assert mal_info["primary"]["name"] == "small"
    assert mal_info["primary"]["id_col_name"] == "InstrID"


def test_dups(cli_link_small_with_dups):
    mal = MergeableAnchoredList.from_excel(cli_link_small_with_dups)

    # print(mal)

    dups = mal.get_duplicates()

    assert len(dups["instr2_all"]) == 12
    assert len(dups["instr3_all"]) == 17
