import click

from macpie.collections.mergeableanchoredlist import MergeableAnchoredList
from macpie.io.excel import MACPieExcelWriter

from macpie.cli.core import ClickPath


@click.command()
@click.option('--keep-original/--no-keep-original',
              default=True)
@click.argument('primary',
                nargs=1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=False))
@click.pass_context
def merge(ctx, keep_original, primary):
    invoker = ctx.obj
    invoker.command_name = ctx.info_name
    invoker.add_opt('keep_original', keep_original)
    invoker.add_arg('primary', primary)

    cmd = _MergeCommand(
        invoker.get_opt('verbose'),
        invoker.get_opt('id_col'),
        invoker.get_opt('date_col'),
        invoker.get_opt('id2_col'),
        invoker.get_opt('keep_original'),
        invoker.get_arg('primary')
    )

    collection = cmd.execute()

    with MACPieExcelWriter(invoker.results_file) as writer:
        collection.to_excel(writer, merge=True)


class _MergeCommand:

    def __init__(
        self,
        verbose,
        id_col,
        date_col,
        id2_col,
        keep_original,
        primary
    ) -> None:
        self.verbose = verbose
        self.id_col = id_col
        self.date_col = date_col
        self.id2_col = id2_col
        self.keep_original = keep_original
        self.primary = primary

    def execute(self):
        collection = MergeableAnchoredList.from_excel(self.primary)
        return collection
