import pathlib
from collections import namedtuple

import click
import pandas as pd

import macpie as mp
from macpie.cli.core import ResultsResource

possible_engines = ["pandas", "tablib"]


FilePairInfo = namedtuple("FilePairInfo", ["file_pair", "sheet_pairs", "filter_kwargs"])


@click.group(chain=True)
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-s", "--sheet", multiple=True)
@click.option("-p", "--sheet-pair", nargs=2, multiple=True)
@click.option("-n", "--filter-name", type=str, multiple=True)
@click.option("-l", "--filter-like", type=str)
@click.option("-r", "--filter-regex", type=str)
@click.option("-i", "--filter-invert", is_flag=True)
@click.argument(
    "files",
    nargs=2,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, path_type=pathlib.Path
    ),
)
@click.pass_context
def main(
    ctx, verbose, sheet, sheet_pair, filter_name, filter_like, filter_regex, filter_invert, files
):
    """This script processes a pair of files. One command feeds into the next."""


@main.result_callback()
@click.pass_context
def process_commands(
    ctx,
    processors,
    verbose,
    sheet,
    sheet_pair,
    filter_name,
    filter_like,
    filter_regex,
    filter_invert,
    files,
):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    rr = ResultsResource(ctx=ctx, verbose=verbose)
    rr.create_results_dir()
    ctx.obj = ctx.with_resource(rr)

    sheet_pairs = process_sheet_options(files, sheet, sheet_pair)

    filter_kwargs = {
        "items": filter_name,
        "like": filter_like,
        "regex": filter_regex,
        "invert": filter_invert,
    }
    if not any(filter_kwargs.values()):
        filter_kwargs = {}

    stream = FilePairInfo(files, sheet_pairs, filter_kwargs)

    # Pipe it through all stream processors.
    for processor in processors:
        stream = processor(stream)

    # Evaluate the stream and throw away the items.
    for _ in stream:
        pass


def process_sheet_options(pair, sheet, sheet_pair):
    left_file, right_file = pair

    sheet_pairs = []

    if sheet:
        for s in sheet:
            sheet_pairs.append((s, s))

    if sheet_pair:
        for sp in sheet_pair:
            sheet_pairs.append(sp)

    if not sheet_pairs:
        left_sheets = mp.openpyxltools.get_sheet_names(left_file)
        right_sheets = mp.openpyxltools.get_sheet_names(right_file)
        ((common_sheets, _), _) = mp.lltools.filter_seq_pair(
            left_sheets, right_sheets, intersection=True
        )
        for cs in common_sheets:
            sheet_pairs.append((cs, cs))
        if not sheet_pairs:
            sheet_pairs.append((left_sheets[0], right_sheets[0]))

    return sheet_pairs


def echo_command_info(title, file_pair_info: FilePairInfo):
    (left_file, right_file), _, _ = file_pair_info
    click.echo()
    click.secho(title, bold=True, bg="green", fg="black")
    click.secho(f"'{left_file.resolve()}'", bold=True)
    click.echo("to")
    click.secho(f"'{right_file.resolve()}'\n", bold=True)


def iter_df_pairs(left_file, right_file, sheet_pairs, filter_kwargs={}):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    left_dfs_dict = pd.read_excel(left_file, sheet_name=left_sheets)
    right_dfs_dict = pd.read_excel(right_file, sheet_name=right_sheets)

    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_df = left_dfs_dict[left_sheetname]
        right_df = right_dfs_dict[right_sheetname]
        if filter_kwargs:
            left_df, right_df = mp.pandas.subset_pair(
                left_df, right_df, filter_kwargs=filter_kwargs
            )
        yield ((left_df, right_df), (left_sheetname, right_sheetname))


def iter_tl_pairs(left_file, right_file, sheet_pairs, filter_kwargs={}):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    with mp.MACPieExcelFile(left_file) as reader:
        left_tlsets_dict = reader.parse_tablib_datasets(sheet_name=left_sheets)

    with mp.MACPieExcelFile(right_file) as reader:
        right_tlsets_dict = reader.parse_tablib_datasets(sheet_name=right_sheets)

    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_tl = left_tlsets_dict[left_sheetname]
        right_tl = right_tlsets_dict[right_sheetname]
        if filter_kwargs:
            left_tl, right_tl = mp.tablibtools.subset_pair(
                left_tl, right_tl, filter_kwargs=filter_kwargs
            )
        yield ((left_tl, right_tl), (left_sheetname, right_sheetname))


from .compare import compare
from .conform import conform

main.add_command(compare)
main.add_command(conform)
