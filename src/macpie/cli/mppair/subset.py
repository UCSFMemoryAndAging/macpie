import click

import macpie as mp
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor, SingletonExcelWriter

from .helpers import echo_command_info, FilePairInfo, iter_df_pairs


@click.command()
@pipeline_processor
@pass_results_resource
def subset(results_resource, file_pair_info):
    """Subset a pair of files and output the differences.

    Example:
    \b
        mppair -i col1 -i col2 file1.xlsx file2.xlsx subset
    """

    (left_file, right_file), sheet_pairs, filter_kwargs = file_pair_info

    echo_command_info("Subsetting", file_pair_info)

    left_results_path = results_resource.results_dir / ("subsetted_" + left_file.name)
    right_results_path = results_resource.results_dir / ("subsetted_" + right_file.name)

    with SingletonExcelWriter(left_results_path) as left_writer, SingletonExcelWriter(
        right_results_path
    ) as right_writer:
        for (left_df, right_df), (left_sheetname, right_sheetname) in iter_df_pairs(
            left_file, right_file, sheet_pairs
        ):
            click.echo(f"Subsetting excel worksheet pair: ({left_sheetname}, {right_sheetname})")
            (left_df, right_df) = mp.pandas.subset_pair(left_df, right_df, **filter_kwargs)
            left_df.to_excel(left_writer(), sheet_name=left_sheetname, index=False)
            right_df.to_excel(right_writer(), sheet_name=right_sheetname, index=False)

    click.echo()
    click.secho("Subsetted results files:", bold=True)
    click.echo(f"{left_results_path.resolve()}")
    click.echo(f"{right_results_path.resolve()}")

    return FilePairInfo((left_results_path, right_results_path), sheet_pairs, filter_kwargs)
