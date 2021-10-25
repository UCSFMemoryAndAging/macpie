import click

from .dbconnections import mysql_connector_connection
from .helpers import show_create_table


@click.command()
@click.argument("tablename", nargs=1)
@click.pass_obj
def createtable(db_cfg, tablename):
    with mysql_connector_connection(db_cfg) as cnx:
        create_table_str = show_create_table(cnx, tablename)

    click.echo(f"DROP TABLE IF EXISTS `{tablename}`;")
    click.echo(create_table_str + ";")
