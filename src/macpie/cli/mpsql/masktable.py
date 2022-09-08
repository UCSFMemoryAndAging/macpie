# TODO: UNFINISHED

from pathlib import Path

import click
import pandas as pd

from macpie.tools import pathtools
from macpie.util import MaskMap, Masker

from macpie.cli.macpie.masker import masker_params

from .dbconnections import mysql_connector_connection, sqlalchemy_connection
from .helpers import execute_multiline_query, show_create_table, transform_table


@click.command()
@masker_params
@click.option(
    "--masked-tablename",
    type=str,
    help="A masked name for the table.",
)
@click.argument("tablename", nargs=1)
@click.pass_obj
def masktable(
    db_cfg,
    tablename,
    masked_tablename,
    random_seed,
    id_cols,
    id_range,
    date_cols,
    id2_range,
    id2_cols,
    cols_no_rename,
    cols_to_drop,
    output_id_maps,
):
    if not masked_tablename:
        masked_tablename = tablename

    mask_map_1 = MaskMap.from_id_range(id_range[0], id_range[1], random_seed=random_seed)
    mask_map_2 = MaskMap.from_id_range(
        id2_range[0], id2_range[1], day_shift=False, random_seed=random_seed
    )

    masker = Masker(mask_map_1, id_cols, date_col_names=date_cols)
    masker.add(mask_map_2, id2_cols)

    with sqlalchemy_connection(db_cfg) as cnx:
        table_df = pd.read_sql_table(tablename, cnx)
        _, col_transformations = masker.mask_df(
            table_df, drop_cols=cols_to_drop, norename_cols=cols_no_rename, inplace=True
        )

    with mysql_connector_connection(db_cfg) as cnx:
        orig_table_def = show_create_table(cnx, tablename)
        new_table_def = transform_table(orig_table_def, col_transformations, masked_tablename)
        execute_multiline_query(db_cfg, new_table_def)

    output_dir = Path(".")
    results_dir = pathtools.create_dir_with_datetime(dir_name_prefix="results_", where=output_dir)

    sql_script = results_dir / (masked_tablename + ".sql")
    with open(sql_script, "w") as f:
        f.write(new_table_def)

    table_df.to_csv(results_dir / (masked_tablename + ".csv"), header=True, index=False)


def create_table(cnx, table_def):
    raw_cnx = cnx.connection
    cur = raw_cnx.cursor()
    cur.execute(table_def, multi=True)


def execute_file(cnx, filepath):
    with open(filepath) as f:
        query = sqlalchemy.sql.text(f.read())

    print("execute file")
    print(query)
    raw_cnx = cnx.connection
    cur = raw_cnx.cursor()
    cur.execute(query)
