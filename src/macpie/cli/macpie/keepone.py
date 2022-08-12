import pathlib

import click

from macpie import BasicList, Dataset, MACPieExcelWriter, pathtools
from macpie._config import get_option
from macpie.cli.core import allowed_path, pass_results_resource
from macpie.cli.helpers import get_client_system_info


@click.command()
@click.option(
    "-k",
    "--keep",
    default="all",
    type=click.Choice(
        ["all", "earliest", "latest"],
        case_sensitive=False,
    ),
)
@click.argument(
    "primary",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@pass_results_resource
def keepone(results_resource, keep, primary):
    """
    This command groups rows that have the same :option:`--id2-col` value, and
    allows you to keep only the earliest or latest row in each group as
    determined by the :option:`--date-col` values (discarding the other rows
    in the group).

    primary : pathlib.Path
        A file path
    """

    # validate
    primary_valid, primary_invalid = pathtools.validate_paths(primary, allowed_path)

    for p in primary_invalid:
        click.echo(f"WARNING: Ignoring invalid file: {p}")

    if len(primary_valid) < 1:
        raise click.UsageError("ERROR: No valid files.")

    primary = primary_valid

    collection = BasicList()
    for filepath in primary:
        dset = Dataset.from_file(
            filepath,
            id_col_name=results_resource.ctx.params["id_col"],
            date_col_name=results_resource.ctx.params["date_col"],
            id2_col_name=results_resource.ctx.params["id2_col"],
            name=filepath.stem,
        )

        dset = dset.group_by_keep_one(keep=keep, drop_duplicates=False)

        if get_option("column.system.duplicates") in dset.columns:
            dset.add_tag(Dataset.tag_duplicates)

        collection.append(dset)

    with MACPieExcelWriter(results_resource.create_results_filepath()) as writer:
        collection.to_excel(writer)
        results_resource.get_command_info().to_excel(writer)
        get_client_system_info().to_excel(writer)
