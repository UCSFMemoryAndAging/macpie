from functools import partial
from pathlib import Path

from macpie.pandas import group_by_keep_one
from macpie.core.dataset import LavaDataset
from macpie.collections.executablegraph import ExecutableGraph

data_dir = Path("tests/data/").resolve()
current_dir = Path(__file__).parent.absolute()


def test_basic():

    dset1 = LavaDataset.from_file(
        current_dir / "pidn_date_1.xlsx",
        name="pidn_date_1"
    )

    dset2 = LavaDataset.from_file(
        current_dir / "pidn_date_2.xlsx",
        name="pidn_date_2"
    )

    dset3 = LavaDataset.from_file(
        current_dir / "pidn_date_3.xlsx",
        name="pidn_date_3"
    )

    G = ExecutableGraph()

    # no nodes
    assert G.g.number_of_nodes() == 0

    G.add_node(
        dset1,
        operation=partial(group_by_keep_one,
                          group_by_col=dset1.id2_col,
                          date_col=dset1.date_col,
                          keep='earliest',
                          drop_duplicates=False)
    )

    G.add_node(dset2)

    G.add_node(dset3)

    assert G.g.number_of_nodes() == 3

    G.add_edge(
        dset1,
        dset2
    )

    G.add_edge(
        dset1,
        dset3
    )

    assert G.get_root_node().name == "pidn_date_1"

    assert G.g.edges[dset1, dset2]['name'] == dset1.name + "->" + dset2.name

    assert G.g.number_of_edges() == 2

    nodes_with_operations = G.get_all_node_data('operation')
    assert len(nodes_with_operations) == 1

    edges_with_names = G.get_all_edge_data('name')
    assert len(edges_with_names) == 2

    G.execute()

    assert G.get_node(dset1)['name'] == 'pidn_date_1'

    assert G.get_node(dset1, 'name') == 'pidn_date_1'
