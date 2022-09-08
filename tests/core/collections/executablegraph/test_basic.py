from functools import partial
from pathlib import Path

import macpie as mp
from macpie.core.collections.graph import ExecutableGraph


THIS_DIR = Path(__file__).parent.absolute()


def test_basic():

    dset1 = mp.LavaDataset.from_file(THIS_DIR / "pidn_date_1.xlsx", name="pidn_date_1")

    dset2 = mp.LavaDataset.from_file(THIS_DIR / "pidn_date_2.xlsx", name="pidn_date_2")

    dset3 = mp.LavaDataset.from_file(THIS_DIR / "pidn_date_3.xlsx", name="pidn_date_3")

    G = ExecutableGraph()

    # no nodes
    assert G.g.number_of_nodes() == 0

    G.add_node(
        dset1,
        operation=partial(
            mp.pandas.group_by_keep_one,
            group_by_col=dset1.id2_col_name,
            date_col_name=dset1.date_col_name,
            keep="earliest",
            drop_duplicates=False,
        ),
    )

    G.add_node(dset2)

    G.add_node(dset3)

    assert G.g.number_of_nodes() == 3

    G.add_edge(dset1, dset2)

    G.add_edge(dset1, dset3)

    assert G.get_root_node().name == "pidn_date_1"

    assert G.g.edges[dset1, dset2]["name"] == dset1.name + "->" + dset2.name

    assert G.g.number_of_edges() == 2

    nodes_with_operations = G.get_all_node_data("operation")
    assert len(nodes_with_operations) == 1

    edges_with_names = G.get_all_edge_data("name")
    assert len(edges_with_names) == 2

    G.execute()

    assert G.get_node(dset1)["name"] == "pidn_date_1"

    assert G.get_node(dset1, "name") == "pidn_date_1"
