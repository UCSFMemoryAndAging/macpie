import click

from .dbconnections import mysql_connector_connection
from .helpers import show_create_procedure


@click.command()
@click.argument("procname", nargs=1)
@click.pass_obj
def createproc(db_cfg, procname):
    with mysql_connector_connection(db_cfg) as cnx:
        create_proc_str = show_create_procedure(cnx, procname)

    header = (
        "\n"
        "-- -----------------------------------------------------------------\n"
        f"-- procedure {procname}\n"
        "-- -----------------------------------------------------------------\n"
        "\n"
        f"DROP PROCEDURE IF EXISTS `{procname}`;\n\n"
        "DELIMITER $$\n\n"
    )

    footer = "\n\n$$\n" "DELIMITER ;\n"

    click.echo(header + create_proc_str + footer)
