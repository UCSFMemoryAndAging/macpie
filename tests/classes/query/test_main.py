from functools import partial
from pathlib import Path

import networkx as nx
import pytest

from macpie.classes import LavaDataObject, Query
from macpie.pandas import group_by_keep_one


current_dir = Path("tests/classes/query/")


def test_query():

    do1 = LavaDataObject.from_file(
        current_dir / "pidn_date_1.xlsx",
        "pidn_date_1"
    )

    do2 = LavaDataObject.from_file(
        current_dir / "pidn_date_2.xlsx",
        "pidn_date_2"
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
        operation=partial(group_by_keep_one,
                          group_by_col=do1.id2_col,
                          date_col=do1.date_col,
                          keep='first',
                          drop_duplicates=False
                          )
    )

    Q.add_node(do2)

    assert Q.g.number_of_nodes() == 2

    Q.add_edge(
        do1,
        do2
    )

    assert Q.get_root_node().name == "pidn_date_1"

    assert Q.g.edges[do1, do2]['name'] == do1.name + "->" + do2.name

    assert Q.g.number_of_edges() == 1

    # need to run Q.execute() before writing to excel
    with pytest.raises(RuntimeError):
        Q.write_excel_cli_basic()

    Q.execute()
    # Q.write_excel_cli_basic(output_dir=current_dir)
