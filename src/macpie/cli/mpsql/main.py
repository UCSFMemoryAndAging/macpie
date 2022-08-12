import os

import click

from .createproc import createproc
from .createtable import createtable
from .masktable import masktable


def validate_password(ctx, param, value):
    if value:
        return click.prompt("Password", hide_input=True)
    else:
        value = os.environ.get("MACPIE_MYSQL_PWD")
        if not value:
            raise click.UsageError(
                "Invalid password. Could not find environment variable 'MACPIE_MYSQL_PWD'. "
                "Either set that environment variable (see documentation for details), "
                f"or specify the {param.get_error_hint(ctx)} flag to type in password via prompt."
            )

    return value


@click.group()
@click.option(
    "-h",
    "--host",
    default="localhost",
    help="Host address of the database.",
)
@click.option(
    "-P",
    "--port",
    default=3306,
    type=int,
    help="Port number to use for connection. Honors " "$MYSQL_TCP_PORT.",
)
@click.option(
    "-u",
    "--user",
    help="User name to connect to the database.",
)
@click.option(
    "-p",
    "--password",
    is_flag="True",
    callback=validate_password,
    help="Password to connect to the database.",
)
@click.argument("database", default="lava_mac_dev", nargs=1)
@click.pass_context
def main(ctx, host, port, user, password, database):
    ctx.obj = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


main.add_command(createproc)
main.add_command(createtable)
main.add_command(masktable)
