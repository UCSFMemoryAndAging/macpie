import pathlib

import click

from macpie.cli.helpers import create_envfile


@click.command()
@click.pass_context
def envfile(ctx):
    create_envfile(ctx)
