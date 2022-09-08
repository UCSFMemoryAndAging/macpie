import collections
import pathlib

import click
import pandas as pd

import macpie as mp
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor

from .main import FilePairSheetPairs

POSSIBLE_ENGINES = ["pandas", "tablib"]


@click.command()
@click.option("-i", "--item", type=str, multiple=True)
@click.option("-l", "--like", type=str)
@click.option("-r", "--regex", type=str)
@click.option("-n", "--invert", is_flag=True)
@click.option(
    "-a",
    "--axis",
    type=click.Choice(["index", "columns"], case_sensitive=False),
    default="columns",
)
@pipeline_processor
@pass_results_resource
def compare(results_resource, file_pair_sheet_pairs, item, like, regex, invert, axis):
    """Compare a pair of files and output the differences."""

    (left_file, right_file), sheet_pairs = file_pair_sheet_pairs

    results_filename = (
        left_file.stem
        + "_"
        + right_file.stem
        + "_diffs_"
        + mp.datetimetools.current_datetime_str()
        + ".xlsx"
    )
    results_path = results_resource.results_dir / results_filename

    # singleton excel_writer
    class excel_writer:
        instance = None

        def __new__(cls):
            if cls.instance is None:
                cls.instance = mp.MACPieExcelWriter(
                    results_path,
                )
            return cls.instance

    filter_kwargs = {
        "items": item,
        "like": like,
        "regex": regex,
        "invert": invert,
    }
    if any(filter_kwargs.values()):
        filter_kwargs = {"filter_kwargs": filter_kwargs}
    else:
        filter_kwargs = None

    dfs_results = compare_files_as_dataframes(
        left_file, right_file, sheet_pairs, filter_kwargs=filter_kwargs
    )

    for sheetname, df in dfs_results.items():
        click.secho(sheetname, bg="blue", fg="white", bold=True)
        click.echo()
        df.to_excel(excel_writer(), sheet_name=sheetname)

    if excel_writer.instance is None:
        click.echo("No differences found.")
    else:
        excel_writer().close()
        click.secho(f"\nResults output to: {results_path.resolve()}\n", bold=True)

    return file_pair_sheet_pairs


def compare_files_as_dataframes(left_file, right_file, sheet_pairs, filter_kwargs={}):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    left_dfs_dict = pd.read_excel(left_file, sheet_name=left_sheets)
    right_dfs_dict = pd.read_excel(right_file, sheet_name=right_sheets)

    dfs_results = collections.OrderedDict()
    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_df = left_dfs_dict[left_sheetname]
        right_df = right_dfs_dict[right_sheetname]

        diffs_df = left_df.mac.compare(right_df, filter_kwargs=filter_kwargs)

        if not diffs_df.empty:
            result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
                "df" + "|" + left_sheetname + "|" + right_sheetname
            )
            dfs_results[result_sheetname] = diffs_df

    return dfs_results
