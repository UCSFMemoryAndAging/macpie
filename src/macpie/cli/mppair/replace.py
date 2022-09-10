import click

from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor
from macpie.cli.macpie.replace import replace_params, replace_in_files

from .main import echo_command_info, FilePairInfo


@click.command()
@replace_params
@pipeline_processor
@pass_results_resource
def replace(
    results_resource,
    file_pair_info,
    to_replace,
    value,
    ignorecase,
    regex,
    re_dotall,
):
    """Loads one or multiple images for processing.  The input parameter
    can be specified multiple times to load more than one image.
    """
    (left_file, right_file), sheet_pairs, filter_kwargs = file_pair_info

    echo_command_info("Replacing values", file_pair_info)

    result_filepaths = replace_in_files(
        results_resource, [left_file, right_file], to_replace, value, ignorecase, regex, re_dotall
    )

    left_results_path, right_results_path = result_filepaths

    click.echo()
    click.secho("Result files with replaced values:", bold=True)
    click.echo(f"{left_results_path.resolve()}")
    click.echo(f"{right_results_path.resolve()}")

    return FilePairInfo((left_results_path, right_results_path), sheet_pairs, filter_kwargs)
