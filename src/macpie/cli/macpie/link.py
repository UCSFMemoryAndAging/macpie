import pathlib

import click

from macpie import Dataset, MACPieExcelWriter, MergeableAnchoredList, pathtools
from macpie._config import get_option
from macpie.cli.common import allowed_path

from ._common import _BaseCommand

NEW_ID_COL_NAME = "link_id"


@click.command()
@click.option(
    "-k",
    "--primary-keep",
    default="all",
    type=click.Choice(["all", "earliest", "latest"], case_sensitive=False),
)
@click.option(
    "-g",
    "--secondary-get",
    default="all",
    type=click.Choice(["all", "closest"], case_sensitive=False),
)
@click.option("-t", "--secondary-days", default=90)
@click.option(
    "-w",
    "--secondary-when",
    default="earlier_or_later",
    type=click.Choice(["earlier", "later", "earlier_or_later"], case_sensitive=False),
)
@click.option(
    "-i",
    "--secondary-id-col",
    default=get_option("dataset.id_col_name"),
    help="Secondary ID Column Header",
)
@click.option(
    "-d",
    "--secondary-date-col",
    default=get_option("dataset.date_col_name"),
    help="Secondary Date Column Header",
)
@click.option(
    "-j",
    "--secondary-id2-col",
    default=get_option("dataset.id2_col_name"),
    help="Secondary ID2 Column Header",
)
@click.option("--merge-results/--no-merge-results", default=True)
@click.option("--keep-original/--no-keep-original", default=False)
@click.argument(
    "primary",
    nargs=1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@click.argument(
    "secondary",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@click.pass_context
def link(
    ctx,
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
    secondary,
):
    """
    Link command

    """
    command_meta = ctx.obj
    command_meta.command_name = ctx.info_name
    command_meta.add_opt("primary_keep", primary_keep)
    command_meta.add_opt("secondary_get", secondary_get)
    command_meta.add_opt("secondary_days", secondary_days)
    command_meta.add_opt("secondary_when", secondary_when)
    command_meta.add_opt("secondary_id_col", secondary_id_col)
    command_meta.add_opt("secondary_date_col", secondary_date_col)
    command_meta.add_opt("secondary_id2_col", secondary_id2_col)
    command_meta.add_opt("merge_results", merge_results)
    command_meta.add_opt("keep_original", keep_original)
    command_meta.add_arg("primary", primary)
    command_meta.add_arg("secondary", secondary)

    cmd = _LinkCommand(command_meta)
    cmd.run_all()

    msg = (
        "\nNOTE: If you want to merge/filter fields from the linked data in the "
        "above results file, perform the following steps:\n"
        "\t1. Open the results file and go to the "
        f'"{MergeableAnchoredList.available_fields_sheetname}" worksheet\n'
        f'\t2. In the column labeled "{MergeableAnchoredList.to_merge_column_name}", '
        'mark an "x" in each field you want to merge/keep\n'
        "\t3. Save the file\n"
        '\t4. Execute this command: "macpie merge FILE", '
        "where FILE is the file you just saved.\n"
        "\t5. A new results file will be created containing the merged results\n"
    )
    click.echo(msg)


class _LinkCommand(_BaseCommand):
    def __init__(self, command_meta) -> None:
        super().__init__(command_meta)

        self.verbose = command_meta.get_opt("verbose")
        self.id_col = command_meta.get_opt("id_col")
        self.date_col = command_meta.get_opt("date_col")
        self.id2_col = command_meta.get_opt("id2_col")
        self.primary_keep = command_meta.get_opt("primary_keep")
        self.secondary_get = command_meta.get_opt("secondary_get")
        self.secondary_days = command_meta.get_opt("secondary_days")
        self.secondary_when = command_meta.get_opt("secondary_when")
        self.secondary_id_col = command_meta.get_opt("secondary_id_col")
        self.secondary_date_col = command_meta.get_opt("secondary_date_col")
        self.secondary_id2_col = command_meta.get_opt("secondary_id2_col")
        self.merge_results = command_meta.get_opt("merge_results")
        self.keep_original = command_meta.get_opt("keep_original")
        self.primary = command_meta.get_arg("primary")
        self.secondary = command_meta.get_arg("secondary")

        self._validate()

    def execute(self):
        prim_dset = Dataset.from_file(
            self.primary,
            id_col_name=None,
            date_col_name=self.date_col,
            id2_col_name=self.id2_col,
            name=self.primary.stem,
        )

        if self.id_col in prim_dset.columns:
            prim_dset.id_col_name = self.id_col
        else:
            click.echo(
                "\nWARNING: ID Column Header (-i, --id-col) not specified "
                'and default of "InstrID" not found in your PRIMARY file.'
            )
            click.echo(f'         Creating one for you called "{NEW_ID_COL_NAME}"\n')

            prim_dset.create_id_col(col_name=NEW_ID_COL_NAME)

        collection = MergeableAnchoredList(prim_dset)

        if self.secondary:
            for sec in self.secondary:
                try:
                    sec_dset = Dataset.from_file(
                        sec,
                        id_col_name=self.secondary_id_col,
                        date_col_name=self.secondary_date_col,
                        id2_col_name=self.secondary_id2_col,
                        name=sec.stem,
                    )

                    sec_dset_linked = prim_dset.date_proximity(
                        right_dset=sec_dset,
                        get=self.secondary_get,
                        when=self.secondary_when,
                        days=self.secondary_days,
                        merge_suffixes=get_option("operators.binary.column_suffixes"),
                        prepend_level_name=False,
                    )

                    collection.add_secondary(sec_dset_linked)
                except Exception as e:
                    click.echo(f'\nERROR loading secondary dataset "{sec}"\n')
                    click.echo(e)
                    raise (e)

        self.collection = collection

    def output_results(self):
        with MACPieExcelWriter(self.results_file) as writer:
            self.collection.to_excel(writer, merge=self.command_meta.get_opt("merge_results"))
            if self.command_meta.get_opt("verbose") is True:
                self.collection.get_dataset_history_info().to_excel(writer)
            self.command_meta.get_command_info().to_excel(writer)
            self.command_meta.get_client_system_info().to_excel(writer)

    def _validate(self):
        if not allowed_path(self.primary):
            raise click.UsageError(f"ERROR: Invalid primary file: {self.primary}")

        if self.secondary:
            (secondary_valid, secondary_invalid) = pathtools.validate_paths(
                self.secondary, allowed_path
            )

            for sec in secondary_invalid:
                click.echo(f"WARNING: Ignoring invalid file: {sec}")

            if len(secondary_valid) < 1:
                raise click.UsageError("ERROR: No valid files.")
            elif len(secondary_valid) == 1:
                if self.primary == secondary_valid[0]:
                    raise click.UsageError(
                        f"ERROR: Primary file is {self.primary}. No secondary files to link to."
                    )

            self.secondary = secondary_valid
