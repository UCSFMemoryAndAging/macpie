from pathlib import Path

import networkx as nx

import macpie as mp
from macpie.core.collections.graph import BasicGraph


THIS_DIR = Path(__file__).parent.absolute()


def test_basicgraph():

    dset1 = mp.LavaDataset.from_file(THIS_DIR / "pidn_date_1.xlsx", name="pidn_date_1")

    dset2 = mp.LavaDataset.from_file(THIS_DIR / "pidn_date_2.xlsx", name="pidn_date_2")

    dset3 = mp.LavaDataset.from_file(THIS_DIR / "pidn_date_3.xlsx", name="pidn_date_3")

    g = nx.DiGraph()
    G = BasicGraph(g)

    # test init
    assert G.g == g

    G = BasicGraph()

    # no nodes
    assert G.g.number_of_nodes() == 0

    G.add_node(dset1)

    G.add_node(dset2)

    G.add_node(dset3)

    assert G.g.number_of_nodes() == 3

    G.add_edge(dset1, dset2)

    G.add_edge(dset1, dset3)

    assert G.get_root_node().name == "pidn_date_1"

    assert G.g.edges[dset1, dset2]["name"] == dset1.name + "->" + dset2.name

    assert G.g.number_of_edges() == 2

    assert G.get_node(dset1)["name"] == "pidn_date_1"

    assert G.get_node(dset1, "name") == "pidn_date_1"

    # G.print_graph()

    # G.draw_graph()
