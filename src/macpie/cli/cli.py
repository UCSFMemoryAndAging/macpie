from collections import OrderedDict
import platform

import click

from macpie import __version__
from macpie.core import LavaDataObject

from .subcommands.keepone.cli import keepone
from .subcommands.link.cli import link
from .subcommands.merge.cli import merge


@click.group()
@click.option('-v', '--verbose',
              is_flag=True,
              help="Will print verbose messages.")
@click.option('-i', '--id-col',
              default=LavaDataObject.FIELD_ID_COL_VALUE_DEFAULT,
              help="ID Column Header")
@click.option('-d', '--date-col',
              default=LavaDataObject.FIELD_DATE_COL_VALUE_DEFAULT,
              help="Date Column Header")
@click.option('-j', '--id2-col',
              default=LavaDataObject.FIELD_ID2_COL_VALUE_DEFAULT,
              help="ID2 Column Header")
@click.version_option(__version__)
@click.pass_context
def main(ctx, verbose, id_col, date_col, id2_col):
    ctx.ensure_object(dict)

    ctx.obj['system'] = OrderedDict()
    ctx.obj['system']['python_version'] = platform.python_version()
    ctx.obj['system']['platform'] = platform.platform()
    ctx.obj['system']['computer_network_name'] = platform.node()

    ctx.obj['options'] = OrderedDict()
    ctx.obj['args'] = OrderedDict()

    ctx.obj['options']['verbose'] = verbose
    ctx.obj['options']['id_col'] = id_col
    ctx.obj['options']['date_col'] = date_col
    ctx.obj['options']['id2_col'] = id2_col


main.add_command(keepone)
main.add_command(link)
main.add_command(merge)
