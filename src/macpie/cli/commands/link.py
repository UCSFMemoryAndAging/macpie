import click

from macpie._config import get_option
from macpie.collections.mergeableanchoredlist import MergeableAnchoredList
from macpie.core.dataset import Dataset
from macpie.exceptions import DatasetIDColError, DateProximityError
from macpie.io.excel import MACPieExcelWriter
from macpie.tools import path as pathtools

from macpie.cli.core import allowed_file, ClickPath


@click.command()
@click.option('-k', '--primary-keep',
              default='all',
              type=click.Choice(['all', 'earliest', 'latest'], case_sensitive=False))
@click.option('-g', '--secondary-get',
              default='all',
              type=click.Choice(['all', 'closest'], case_sensitive=False))
@click.option('-t', '--secondary-days',
              default=90)
@click.option('-w', '--secondary-when',
              default='earlier_or_later',
              type=click.Choice(['earlier', 'later', 'earlier_or_later'], case_sensitive=False))
@click.option('-i', '--secondary-id-col',
              default=get_option("dataset.id_col"),
              help="Secondary ID Column Header")
@click.option('-d', '--secondary-date-col',
              default=get_option("dataset.date_col"),
              help="Secondary Date Column Header")
@click.option('-j', '--secondary-id2-col',
              default=get_option("dataset.id2_col"),
              help="Secondary ID2 Column Header")
@click.option('--merge-results/--no-merge-results',
              default=True)
@click.option('--keep-original/--no-keep-original',
              default=False)
@click.argument('primary',
                nargs=1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.argument('secondary',
                nargs=-1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.pass_context
def link(ctx,
         primary_keep,
         secondary_get,
         secondary_days,
         secondary_when,
         secondary_id_col,
         secondary_date_col,
         secondary_id2_col,
         merge_results,
         keep_original,
         primary,
         secondary):
    invoker = ctx.obj
    invoker.command_name = ctx.info_name
    invoker.add_opt('primary_keep', primary_keep)
    invoker.add_opt('secondary_get', secondary_get)
    invoker.add_opt('secondary_days', secondary_days)
    invoker.add_opt('secondary_when', secondary_when)
    invoker.add_opt('secondary_id_col', secondary_id_col)
    invoker.add_opt('secondary_date_col', secondary_date_col)
    invoker.add_opt('secondary_id2_col', secondary_id2_col)
    invoker.add_opt('merge_results', merge_results)
    invoker.add_opt('keep_original', keep_original)
    invoker.add_arg('primary', primary)
    invoker.add_arg('secondary', secondary)

    cmd = _LinkCommand(invoker.get_opt('verbose'),
                       invoker.get_opt('id_col'),
                       invoker.get_opt('date_col'),
                       invoker.get_opt('id2_col'),
                       invoker.get_opt('primary_keep'),
                       invoker.get_opt('secondary_get'),
                       invoker.get_opt('secondary_days'),
                       invoker.get_opt('secondary_when'),
                       invoker.get_opt('secondary_id_col'),
                       invoker.get_opt('secondary_date_col'),
                       invoker.get_opt('secondary_id2_col'),
                       invoker.get_opt('merge_results'),
                       invoker.get_opt('keep_original'),
                       invoker.get_arg('primary'),
                       invoker.get_arg('secondary'))

    collection = cmd.execute()

    with MACPieExcelWriter(invoker.results_file) as writer:
        collection.to_excel(writer, merge=invoker.get_opt('merge_results'))
        if invoker.get_opt('verbose'):
            collection.get_dataset_history_info().to_excel(writer)
        invoker.get_command_info().to_excel(writer)
        invoker.get_client_system_info().to_excel(writer)

    msg = ('\nNOTE: If you want to merge/filter fields from the linked data in the '
           'above results file, perform the following steps:\n'
           '\t1. Open the results file and go to the '
           f'"{get_option("sheet.name.available_fields")}" worksheet\n'
           f'\t2. In the column labeled "{get_option("column.to_merge")}", '
           'mark an "x" in each field you want to merge/keep\n'
           '\t3. Save the file\n'
           '\t4. Execute this command: "macpie merge FILE", '
           'where FILE is the file you just saved.\n'
           '\t5. A new results file will be created containing the merged results\n')

    invoker.add_post_message(msg)


class _LinkCommand:

    def __init__(
        self,
        verbose,
        id_col,
        date_col,
        id2_col,
        primary_keep,
        secondary_get,
        secondary_days,
        secondary_when,
        secondary_id_col,
        secondary_date_col,
        secondary_id2_col,
        merge_results,
        keep_original,
        primary,
        secondary
    ) -> None:
        self.verbose = verbose
        self.id_col = id_col
        self.date_col = date_col
        self.id2_col = id2_col
        self.primary_keep = primary_keep
        self.secondary_get = secondary_get
        self.secondary_days = secondary_days
        self.secondary_when = secondary_when
        self.secondary_id_col = secondary_id_col
        self.secondary_date_col = secondary_date_col
        self.secondary_id2_col = secondary_id2_col
        self.merge_results = merge_results
        self.keep_original = keep_original
        self.primary = primary
        self.secondary = secondary

        self._validate()

    def execute(self):

        try:
            prim_dset = Dataset.from_file(
                self.primary,
                id_col=self.id_col,
                date_col=self.date_col,
                id2_col=self.id2_col,
                name=self.primary.stem
            )
        except DatasetIDColError:
            click.echo('\nWARNING: ID Column Header (-i, --id-col) not specified '
                       'and default of "InstrID" not found in your PRIMARY file.')
            click.echo(f'         Creating one for you called "{get_option("column.link_id")}"\n')

            prim_dset = Dataset.from_file(
                self.primary,
                id_col=None,
                date_col=self.date_col,
                id2_col=self.id2_col,
                name=self.primary.stem
            )

            prim_dset.create_id_col(col_name=get_option("column.link_id"))

        collection = MergeableAnchoredList(prim_dset)

        if self.secondary:
            for sec in self.secondary:
                try:
                    sec_dset = Dataset.from_file(
                        sec,
                        id_col=self.secondary_id_col,
                        date_col=self.secondary_date_col,
                        id2_col=self.secondary_id2_col,
                        name=sec.stem
                    )
                    sec_dset.date_proximity(
                        anchor_dset=prim_dset,
                        get=self.secondary_get,
                        when=self.secondary_when,
                        days=self.secondary_days,
                        merge_suffixes=get_option("operators.binary.column_suffixes")
                    )
                    collection.add_secondary(sec_dset)
                except DateProximityError as dpe:
                    click.echo(f'\nERROR linking secondary dataset "{sec}"\n')
                    click.echo(dpe)
                except Exception as e:
                    click.echo(f'\nERROR loading secondary dataset "{sec}"\n')
                    click.echo(e)
                    raise(e)

        return collection

    def _validate(self):
        self.primary = pathtools.validate_filepath(self.primary, allowed_file)

        if self.secondary:
            (secondary_valid, secondary_invalid) = pathtools.validate_filepaths(self.secondary, allowed_file)

            for sec in secondary_invalid:
                click.echo(f"WARNING: Ignoring invalid file: {sec}")

            if len(secondary_valid) < 1:
                raise click.UsageError("ERROR: No valid files.")
            elif len(secondary_valid) == 1:
                if self.primary == secondary_valid[0]:
                    raise click.UsageError(f"ERROR: Primary file is {self.primary}. No secondary files to link to.")

            self.secondary = secondary_valid
