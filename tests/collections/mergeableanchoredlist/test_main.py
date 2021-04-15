from pathlib import Path

from macpie.collections.mergeableanchoredlist import MergeableAnchoredList


current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None


def test_read_file(cli_link_small_with_merge):
    mal = MergeableAnchoredList.from_excel(cli_link_small_with_merge)

    mal_dict = mal.to_dict()

    assert mal_dict['primary'].name == 'small'
    assert mal_dict['primary'].id_col == 'InstrID'

    mal_info = mal.get_collection_info().to_dict()

    assert mal_info['class_name'] == 'MergeableAnchoredList'
    assert mal_info['primary']['name'] == 'small'
    assert mal_info['primary']['id_col'] == 'InstrID'
