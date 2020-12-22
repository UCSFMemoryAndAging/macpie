from functools import partial
from pathlib import Path

import networkx as nx

from macpie import pandas
from macpie.core import LavaDataObject, Query

current_dir = Path("tests/core/query/").resolve()


def test_query():

    do1 = LavaDataObject.from_file(
        current_dir / "pidn_date_1.xlsx",
        "pidn_date_1"
    )

    do2 = LavaDataObject.from_file(
        current_dir / "pidn_date_2.xlsx",
        "pidn_date_2"
    )

    do3 = LavaDataObject.from_file(
        current_dir / "pidn_date_3.xlsx",
        "pidn_date_3"
    )

    g = nx.DiGraph()
    Q = Query(g)

    # test init
    assert Q.g == g

    Q = Query()

    # no nodes
    assert Q.g.number_of_nodes() == 0

    Q.add_node(
        do1,
        operation=partial(pandas.group_by_keep_one,
                          group_by_col=do1.id2_col,
                          date_col=do1.date_col,
                          keep='earliest',
                          drop_duplicates=False
                          )
    )

    Q.add_node(do2)

    Q.add_node(do3)

    assert Q.g.number_of_nodes() == 3

    Q.add_edge(
        do1,
        do2
    )

    Q.add_edge(
        do1,
        do3
    )

    assert Q.get_root_node().name == "pidn_date_1"

    assert Q.g.edges[do1, do2]['name'] == do1.name + "->" + do2.name

    assert Q.g.number_of_edges() == 2

    nodes_with_operations = Q.get_all_node_data('operation')
    assert len(nodes_with_operations) == 1

    edges_with_names = Q.get_all_edge_data('name')
    assert len(edges_with_names) == 2

    Q.execute()

    assert Q.get_node(do1)['name'] == 'pidn_date_1'

    assert Q.get_node(do1, 'name') == 'pidn_date_1'

    # Q.print_graph()

    # Q.draw_graph()
