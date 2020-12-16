from collections import OrderedDict
from pathlib import Path
from typing import ClassVar

import click
import pandas as pd

from macpie import __version__, io
from macpie.core import Datasheet, LavaDataObject

from macpie.cli.common import get_system_info, iterate_params, print_ctx
from macpie.cli.subcommands.keepone import keepone
from macpie.cli.subcommands.link import link
from macpie.cli.subcommands.merge import merge


class Invoker:

    SHEETNAME_COMMAND_INFO : ClassVar[str] = '_command_info'
    SHEETNAME_SYSTEM_INFO : ClassVar[str] = '_system_info'

    def __init__(self, command_name, opts, args, output_dir: Path = None):
        self.command_name = command_name
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

    def get_command_info(self):
        cli_info_columns = ['command', 'version', 'param_type', 'param_name', 'param_value']
        cli_info_data = []
        cli_info_data.extend([(self.command_name, __version__, 'option') + row for row in iterate_params(self.opts)])
        cli_info_data.extend([(self.command_name, __version__, 'argument') + row for row in iterate_params(self.args)])
        df = pd.DataFrame.from_records(cli_info_data, columns=cli_info_columns)
        return Datasheet(self.SHEETNAME_COMMAND_INFO, df)

    def get_system_info(self):
        system_info_columns = ['param_name', 'param_value']
        system_info_data = [row for row in iterate_params(get_system_info())]
        df = pd.DataFrame.from_records(system_info_data, columns=system_info_columns)
        return Datasheet(self.SHEETNAME_SYSTEM_INFO, df)


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
    command_name = ctx.info_name
    opts = OrderedDict()
    args = OrderedDict()

    opts['verbose'] = verbose
    opts['id_col'] = id_col
    opts['date_col'] = date_col
    opts['id2_col'] = id2_col

    ctx.obj = Invoker(command_name, opts, args)

    @ctx.call_on_close
    def print_summary():
        if verbose:
            print_ctx(ctx)
        click.echo(f'\nLook for results in: {ctx.obj.results_file.resolve()}\n')


main.add_command(keepone)
main.add_command(link)
main.add_command(merge)
