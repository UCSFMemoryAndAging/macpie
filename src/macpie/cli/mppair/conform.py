import click

from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor


@click.command()
@click.option("-c", "--sort-col")
@pipeline_processor
@pass_results_resource
def conform(results_resource, file_pair_sheet_pairs, sort_col):
    """Loads one or multiple images for processing.  The input parameter
    can be specified multiple times to load more than one image.
    """
    print(results_resource.get_command_info())
    return file_pair_sheet_pairs
