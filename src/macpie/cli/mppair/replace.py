import click

from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor


@click.command()
@click.option("-r", "--to-replace", required=True)
@click.option("-v", "--value", required=True)
@click.option("--ignorecase", is_flag=True)
@click.option("--regex", is_flag=True)
@click.option("--re-dotall", is_flag=True)
@pipeline_processor
@pass_results_resource
def replace(
    results_resource, file_pair_sheet_pairs, to_replace, value, ignorecase, regex, re_dotall
):
    """Loads one or multiple images for processing.  The input parameter
    can be specified multiple times to load more than one image.
    """
    return file_pair_sheet_pairs
