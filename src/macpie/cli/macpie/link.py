import pathlib

import click

from macpie import Dataset, MACPieExcelWriter, MergeableAnchoredList, pathtools
from macpie._config import get_option
from macpie.cli.core import allowed_path, pass_results_resource
from macpie.cli.helpers import get_client_system_info

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
@pass_results_resource
def link(
    results_resource,
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
    if not allowed_path(primary):
        raise click.UsageError(f"ERROR: Invalid primary file: {primary}")

    if secondary:
        (secondary_valid, secondary_invalid) = pathtools.validate_paths(secondary, allowed_path)

        for sec in secondary_invalid:
            click.echo(f"WARNING: Ignoring invalid file: {sec}")

        if len(secondary_valid) < 1:
            raise click.UsageError("ERROR: No valid files.")
        elif len(secondary_valid) == 1:
            if primary == secondary_valid[0]:
                raise click.UsageError(
                    f"ERROR: Primary file is {primary}. No secondary files to link to."
                )

        secondary = secondary_valid

    id_col = results_resource.get_param_value("id_col")
    date_col = results_resource.get_param_value("date_col")
    id2_col = results_resource.get_param_value("id2_col")

    prim_dset = Dataset.from_file(
        primary,
        id_col_name=None,
        date_col_name=date_col,
        id2_col_name=id2_col,
        name=primary.stem,
    )

    if id_col in prim_dset.columns:
        prim_dset.id_col_name = id_col
    else:
        click.echo(
            "\nWARNING: ID Column Header (-i, --id-col) not specified "
            'and default of "InstrID" not found in your PRIMARY file.'
        )
        click.echo(f'         Creating one for you called "{NEW_ID_COL_NAME}"\n')

        prim_dset.create_id_col(col_name=NEW_ID_COL_NAME)

    collection = MergeableAnchoredList(prim_dset)

    if secondary:
        for sec in secondary:
            try:
                sec_dset = Dataset.from_file(
                    sec,
                    id_col_name=secondary_id_col,
                    date_col_name=secondary_date_col,
                    id2_col_name=secondary_id2_col,
                    name=sec.stem,
                )

                sec_dset_linked = prim_dset.date_proximity(
                    right_dset=sec_dset,
                    get=secondary_get,
                    when=secondary_when,
                    days=secondary_days,
                    merge_suffixes=get_option("operators.binary.column_suffixes"),
                    prepend_level_name=False,
                )

                collection.add_secondary(sec_dset_linked)
            except Exception as e:
                click.echo(f'\nERROR loading secondary dataset "{sec}"\n')
                click.echo(e)
                raise (e)

    with MACPieExcelWriter(results_resource.create_results_filepath()) as writer:
        collection.to_excel(writer, merge=merge_results)
        if results_resource.verbose:
            collection.get_dataset_history_info().to_excel(writer)
        results_resource.get_command_info().to_excel(writer)
        get_client_system_info().to_excel(writer)

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
