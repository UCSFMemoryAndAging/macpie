from functools import partial

import click
import pandas as pd

from macpie import io, pandas, util
from macpie.core import Databook, Datasheet, LavaDataObject, Query

from macpie.cli.base import ClickPath, CmdParams
from macpie.cli.common import allowed_file, format_basic


@click.command()
@click.option('-k', '--keep',
              default='all',
              type=click.Choice(['all', 'earliest', 'latest'], case_sensitive=False))
@click.argument('primary',
                nargs=-1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.pass_context
def keepone(ctx, keep, primary):
    invoker = ctx.obj
    invoker.command_name = ctx.info_name
    invoker.add_opt('keep', keep)
    invoker.add_arg('primary', primary)

    params = KeepOneCmdParams(invoker.get_opt('verbose'),
                              invoker.get_opt('id_col'),
                              invoker.get_opt('date_col'),
                              invoker.get_opt('id2_col'),
                              invoker.get_opt('keep'),
                              invoker.get_arg('primary'))

    query = KeepOneQuery(params.opts, params.args)
    query.execute_query()

    databook = query.get_results()
    databook.add_metadata_sheet(invoker.get_command_info())
    databook.add_metadata_sheet(invoker.get_system_info())
    databook.to_excel(invoker.results_file)

    format_basic(invoker.results_file)


class KeepOneCmdParams(CmdParams):

    def __init__(self,
                 verbose,
                 id_col,
                 date_col,
                 id2_col,
                 keep,
                 primary) -> None:

        _primary_valid, _primary_invalid = io.validate_filepaths(primary, allowed_file)

        for p in _primary_invalid:
            click.echo(f"WARNING: Ignoring invalid file: {p}")

        if len(_primary_valid) < 1:
            raise click.UsageError("ERROR: No valid files.")

        self._opts = {
            'verbose': verbose,
            'id_col': id_col,
            'date_col': date_col,
            'id2_col': id2_col,
            'keep': keep
        }

        self._args = {
            'primary': _primary_valid
        }

    @property
    def opts(self):
        return self._opts

    @property
    def args(self):
        return self._args


class KeepOneQuery:
    """
    The Receiver classes contain some important business logic. They know how to
    perform all kinds of operations, associated with carrying out a request. In
    fact, any class may serve as a Receiver.
    """

    def __init__(self, opts, args):
        self.opts = opts
        self.args = args
        self.Q = Query()

        primary = args['primary']

        for prim in primary:
            primary_do = LavaDataObject.from_file(
                prim,
                prim.stem,
                id_col=opts['id_col'],
                date_col=opts['date_col'],
                id2_col=opts['id2_col']
            )

            self.Q.add_node(
                primary_do,
                operation=partial(pandas.group_by_keep_one,
                                  group_by_col=primary_do.id2_col,
                                  date_col=primary_do.date_col,
                                  keep=opts['keep'],
                                  drop_duplicates=False)
            )

    def execute_query(self):
        click.echo("Executing query...")
        self.Q.execute()

    def get_results(self):
        db = Databook()
        nodes_with_operations = self.Q.get_all_node_data('operation')
        for node in nodes_with_operations:
            result = node['operation_result']
            db.add_sheet(Datasheet(node['name'], result))

        edges_with_operation_results = self.Q.get_all_edge_data('operation_result')
        for edge in edges_with_operation_results:
            sheetname = edge['name']
            if edge['duplicates']:
                sheetname = util.string.add_suffix(sheetname, "(DUPS)", 31)
            db.add_sheet(Datasheet(sheetname, edge['operation_result']))

        db.add_sheet(Datasheet(Query.SHEETNAME_QUERY_DATAOBJECTS, pd.DataFrame(self.Q.log_dataobjects)))
        db.add_sheet(Datasheet(Query.SHEETNAME_QUERY_OPERATIONS, pd.DataFrame(self.Q.log_operations)))

        return db
