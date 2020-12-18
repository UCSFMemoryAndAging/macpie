from collections import OrderedDict

import click

from macpie.core import LavaDataObject

from macpie.cli.base import Invoker
from macpie.cli.common import get_version, print_ctx
from macpie.cli.subcommands.keepone import keepone
from macpie.cli.subcommands.link import link
from macpie.cli.subcommands.merge import merge


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
@click.version_option(get_version())
@click.pass_context
def main(ctx, verbose, id_col, date_col, id2_col):
    command_name = ctx.info_name
    opts = OrderedDict()
    args = OrderedDict()

    opts['verbose'] = verbose
    opts['id_col'] = id_col
    opts['date_col'] = date_col
    opts['id2_col'] = id2_col

    ctx.obj = Invoker(command_name, opts, args)

    if verbose:
        print_ctx(ctx)

    @ctx.call_on_close
    def on_close():
        ctx.obj.print_post_messages()


main.add_command(keepone)
main.add_command(link)
main.add_command(merge)
