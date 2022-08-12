import pathlib

import click

from macpie import read_excel, MACPieExcelWriter
from macpie.cli.core import pass_results_resource


@click.command()
@click.option("--keep-original/--no-keep-original", default=True)
@click.argument(
    "primary",
    nargs=1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
)
@pass_results_resource
def merge(results_resource, keep_original, primary):
    results = read_excel(primary, as_collection=True)

    with MACPieExcelWriter(results_resource.create_results_filepath()) as writer:
        results.to_excel(writer, merge=True)
