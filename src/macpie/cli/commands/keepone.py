import click

from macpie._config import get_option
from macpie.collections.basiclist import BasicList
from macpie.core.dataset import Dataset
from macpie.io.excel import MACPieExcelWriter
from macpie.tools import path as pathtools

from macpie.cli.core import allowed_file, ClickPath


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

    cmd = _KeepOneCommand(
        invoker.get_opt('verbose'),
        invoker.get_opt('id_col'),
        invoker.get_opt('date_col'),
        invoker.get_opt('id2_col'),
        invoker.get_opt('keep'),
        invoker.get_arg('primary')
    )

    collection = cmd.execute()

    with MACPieExcelWriter(invoker.results_file) as writer:
        collection.to_excel(writer)
        collection.get_collection_info().to_excel(writer)
        invoker.get_command_info().to_excel(writer)
        invoker.get_client_system_info().to_excel(writer)


class _KeepOneCommand:

    def __init__(
        self,
        verbose,
        id_col,
        date_col,
        id2_col,
        keep,
        primary
    ) -> None:
        self.verbose = verbose
        self.id_col = id_col
        self.date_col = date_col
        self.id2_col = id2_col
        self.keep = keep
        self.primary = primary

        self._validate()

    def execute(self):
        collection = BasicList()

        for filepath in self.primary:
            dset = Dataset.from_file(
                filepath,
                id_col=self.id_col,
                date_col=self.date_col,
                id2_col=self.id2_col,
                name=filepath.stem
            )

            dset.group_by_keep_one(keep=self.keep, drop_duplicates=False)
            if get_option("column.system.duplicates") in dset.df.columns:
                dset.add_tag(get_option("dataset.tag.duplicates"))
            collection.append(dset)

        return collection

    def _validate(self):
        primary_valid, primary_invalid = pathtools.validate_filepaths(self.primary, allowed_file)

        for p in primary_invalid:
            click.echo(f"WARNING: Ignoring invalid file: {p}")

        if len(primary_valid) < 1:
            raise click.UsageError("ERROR: No valid files.")

        self.primary = primary_valid
