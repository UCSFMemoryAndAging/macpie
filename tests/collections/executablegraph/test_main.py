from copy import deepcopy
from functools import partial
from pathlib import Path

import pandas as pd
import pytest

from macpie._config import get_option
from macpie.core.dataset import LavaDataset
from macpie.collections.graph import ExecutableGraph
from macpie.pandas import file_to_dataframe
from macpie.pandas.operators.date_proximity import date_proximity
from macpie.pandas.operators.group_by_keep_one import group_by_keep_one


DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path(__file__).parent.absolute()

COL_FILTER_KWARGS = {
    "filter_kwargs": {
        "regex": "^" + get_option("column.system.prefix"),
        "invert": True,
    }
}


@pytest.mark.slow
def test_keepone(cli_keepone_big):
    G = ExecutableGraph()

    prim_filepath = DATA_DIR / "instr1_primaryall.csv"

    primary = LavaDataset.from_file(prim_filepath)

    G.add_node(
        primary,
        operation=partial(
            group_by_keep_one,
            group_by_col=primary.id2_col_name,
            date_col_name=primary.date_col_name,
            keep="earliest",
            drop_duplicates=False,
        ),
    )

    G.execute()

    nodes_with_operations = G.get_all_node_data("operation")

    result = nodes_with_operations[0]["operation_result"]

    expected_result = file_to_dataframe(cli_keepone_big)

    (left, right) = result.mac.conform(
        expected_result, filter_kwargs=COL_FILTER_KWARGS, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)


@pytest.mark.slow
def test_link():
    # macpie link -g closest tests/cli/macpie/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv

    prim = LavaDataset.from_file(Path("tests/cli/macpie/link/small.xlsx"))
    sec_1 = LavaDataset.from_file(Path(DATA_DIR / "instr2_all.csv"))
    sec_2 = LavaDataset.from_file(Path(DATA_DIR / "instr3_all.csv"))

    prim_copy = deepcopy(prim)
    sec_1_copy = deepcopy(sec_1)
    sec_2_copy = deepcopy(sec_2)

    G = ExecutableGraph()

    G.add_node(
        prim,
        operation=partial(
            group_by_keep_one,
            group_by_col=prim.id2_col_name,
            date_col_name=prim.date_col_name,
            keep="all",
            id_col_name=prim.id_col_name,
            drop_duplicates=False,
        ),
    )
    G.add_node(sec_1)
    G.add_node(sec_2)

    G.add_edge(
        prim,
        sec_1,
        operation=partial(
            date_proximity,
            id_left_on=prim.id2_col_name,
            id_right_on=sec_1.id2_col_name,
            date_left_on=prim.date_col_name,
            date_right_on=sec_1.date_col_name,
            get="closest",
            when="earlier_or_later",
            days=90,
            left_link_id=prim.id_col_name,
        ),
    )
    G.add_edge(
        prim,
        sec_2,
        operation=partial(
            date_proximity,
            id_left_on=prim.id2_col_name,
            id_right_on=sec_2.id2_col_name,
            date_left_on=prim.date_col_name,
            date_right_on=sec_2.date_col_name,
            get="closest",
            when="earlier_or_later",
            days=90,
            left_link_id=prim.id_col_name,
        ),
    )

    G.execute()

    edges_with_operation_results = G.get_all_edge_data("operation_result")

    sec_1_copy = prim_copy.date_proximity(
        right_dset=sec_1_copy,
        get="closest",
        when="earlier_or_later",
        days=90,
        prepend_level_name=False,
    )

    (left, right) = sec_1_copy.mac.conform(
        edges_with_operation_results[0]["operation_result"],
        filter_kwargs=COL_FILTER_KWARGS,
        values_order=True,
    )
    pd.testing.assert_frame_equal(left, right)

    sec_2_copy = prim_copy.date_proximity(
        right_dset=sec_2_copy,
        get="closest",
        when="earlier_or_later",
        days=90,
        prepend_level_name=False,
    )

    (left, right) = sec_2_copy.mac.conform(
        edges_with_operation_results[1]["operation_result"],
        filter_kwargs=COL_FILTER_KWARGS,
        values_order=True,
    )
    pd.testing.assert_frame_equal(left, right)
