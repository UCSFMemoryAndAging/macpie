import click

import macpie as mp
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor, SingletonExcelWriter

from .helpers import echo_command_info, FilePairInfo, iter_df_pairs


@click.command()
@click.option("-d", "--data-types", is_flag=True)
@click.option("-i", "--index-order", is_flag=True)
@click.option("-v", "--values-order", is_flag=True)
@pipeline_processor
@pass_results_resource
def conform(results_resource, file_pair_info, data_types, index_order, values_order):
    """Conform a worksheet in one file to "look like" a worksheet in another file.

    Example:
    \b
        mppair file1.xlsx file2.xlsx conform --data-types
    """

    if mp.core.common.count_bool_true(data_types, index_order, values_order) == 0:
        click.echo(
            "At least one of the options must be specified. Try 'conform --help' to view options."
        )
        return file_pair_info

    (left_file, right_file), sheet_pairs, filter_kwargs = file_pair_info

    echo_command_info("Conforming", file_pair_info)

    left_results_path = results_resource.results_dir / ("conformed_" + left_file.name)
    right_results_path = results_resource.results_dir / ("conformed_" + right_file.name)

    with SingletonExcelWriter(left_results_path) as left_writer, SingletonExcelWriter(
        right_results_path
    ) as right_writer:
        for (left_df, right_df), (left_sheetname, right_sheetname) in iter_df_pairs(
            left_file, right_file, sheet_pairs
        ):
            click.echo(f"Conforming excel worksheet pair: ({left_sheetname}, {right_sheetname})")
            (left_df, right_df) = mp.pandas.conform(
                left_df,
                right_df,
                dtypes=data_types,
                index_order=index_order,
                values_order=values_order,
            )
            left_df.to_excel(left_writer(), sheet_name=left_sheetname, index=False)
            right_df.to_excel(right_writer(), sheet_name=right_sheetname, index=False)

    click.echo()
    click.secho("Conformed results files:", bold=True)
    click.echo(f"{left_results_path.resolve()}")
    click.echo(f"{right_results_path.resolve()}")

    return FilePairInfo((left_results_path, right_results_path), sheet_pairs, filter_kwargs)
