import click

import macpie as mp
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor, SingletonExcelWriter

from .main import iter_df_pairs


@click.command()
@click.option("-d", "--data-types", is_flag=True)
@click.option("-i", "--index-order", is_flag=True)
@click.option("-v", "--values-order", is_flag=True)
@pipeline_processor
@pass_results_resource
def conform(results_resource, file_pair_info, data_types, index_order, values_order):
    """Conform a worksheet in one file to "look like" a worksheet in another file.

    Examples
    --------
    mppair file1.xlsx file2.xlsx conform
    """
    if mp.core.common.count_bool_true(data_types, index_order, values_order) == 0:
        click.echo(
            "At least one of the options must be specified. Try 'conform --help' to view options."
        )
        return file_pair_info

    (left_file, right_file), sheet_pairs, filter_kwargs = file_pair_info

    results_dir = results_resource.create_results_dir()

    left_results_path = results_dir / left_file.name
    right_results_path = results_dir / right_file.name

    with SingletonExcelWriter(left_results_path) as left_writer, SingletonExcelWriter(
        right_results_path
    ) as right_writer:
        for (left_df, right_df), (left_sheetname, right_sheetname) in iter_df_pairs(
            left_file, right_file, sheet_pairs, filter_kwargs=filter_kwargs
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

    return file_pair_info
