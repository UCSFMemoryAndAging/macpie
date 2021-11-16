import abc
import collections
import json
import platform
from pathlib import Path

import click

from macpie import __version__, pathtools, tablibtools, MACPieJSONEncoder
from macpie._config import get_option

from ._common import CommandMeta


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-i", "--id-col", default=get_option("dataset.id_col_name"), help="ID Column Header")
@click.option(
    "-d", "--date-col", default=get_option("dataset.date_col_name"), help="Date Column Header"
)
@click.option(
    "-j", "--id2-col", default=get_option("dataset.id2_col_name"), help="ID2 Column Header"
)
@click.version_option(__version__)
@click.pass_context
def main(ctx, verbose, id_col, date_col, id2_col):
    command_meta = CommandMeta(ctx.info_name)
    command_meta.add_opt("verbose", verbose)
    command_meta.add_opt("id_col", id_col)
    command_meta.add_opt("date_col", date_col)
    command_meta.add_opt("id2_col", id2_col)

    ctx.obj = command_meta


from .keepone import keepone
from .link import link
from .masker import masker
from .merge import merge

main.add_command(keepone)
main.add_command(link)
main.add_command(masker)
main.add_command(merge)
