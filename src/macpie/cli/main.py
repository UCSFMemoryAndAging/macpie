from collections import OrderedDict
from pathlib import Path

import click

from macpie import __version__, io
from macpie.core import LavaDataObject

from macpie.cli.common import print_ctx
from macpie.cli.subcommands.keepone import keepone
from macpie.cli.subcommands.link import link
from macpie.cli.subcommands.merge import merge


class Invoker:

    def __init__(self, opts, args, output_dir: Path = None):
        self.opts = opts
        self.args = args

        self.output_dir = output_dir or Path('.')
        self.results_dir = io.create_output_dir(output_dir, "results")
        self.results_file = self.results_dir / (self.results_dir.stem + '.xlsx')

    def add_opt(self, k, v):
        self.opts[k] = v

    def get_opt(self, k):
        return self.opts[k]

    def add_arg(self, k, v):
        self.args[k] = v

    def get_arg(self, k):
        return self.args[k]


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
    opts = OrderedDict()
    args = OrderedDict()

    opts['verbose'] = verbose
    opts['id_col'] = id_col
    opts['date_col'] = date_col
    opts['id2_col'] = id2_col

    ctx.obj = Invoker(opts, args)

    @ctx.call_on_close
    def print_summary():
        if verbose:
            print_ctx(ctx)
        click.echo(f'\nLook for results in: {ctx.obj.results_file.resolve()}\n')


main.add_command(keepone)
main.add_command(link)
main.add_command(merge)
