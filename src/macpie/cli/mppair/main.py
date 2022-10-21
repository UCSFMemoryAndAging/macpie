import pathlib

import click

import macpie as mp
from macpie.cli.core import ResultsResource

from .helpers import FilePairInfo


@click.group(chain=True)
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-s", "--sheet", multiple=True)
@click.option("-p", "--sheet-pair", nargs=2, multiple=True)
@click.option("-n", "--filter-name", type=str, multiple=True)
@click.option("-l", "--filter-like", type=str)
@click.option("-r", "--filter-regex", type=str)
@click.option("-i", "--filter-invert", is_flag=True)
@click.option("-x", "--filter-intersection", is_flag=True)
@click.argument(
    "files",
    nargs=2,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, path_type=pathlib.Path
    ),
)
@click.pass_context
def main(
    ctx,
    verbose,
    sheet,
    sheet_pair,
    filter_name,
    filter_like,
    filter_regex,
    filter_invert,
    filter_intersection,
    files,
):
    """
    This command processes a pair of files via one or more subcommands. One subcommand
    feeds into the next.

    Example:
    \b
        mppair -i col1 -i col2 file1.xlsx file2.xlsx conform replace compare
    """


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
    filter_intersection,
    files,
):
    """This result callback is invoked with an iterable of all the chained
    subcommands. Because each subcommand returns a function,
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.

    Adapted From: https://github.com/pallets/click/blob/fb4327216543d751e2654a0d3bf6ce3d31c435cc/examples/imagepipe/imagepipe.py#L24
    """
    rr = ResultsResource(ctx=ctx, verbose=verbose)
    rr.create_results_dir()  # to be shared among all subcommands
    ctx.obj = ctx.with_resource(rr)

    sheet_pairs = process_sheet_options(files, sheet, sheet_pair)

    filter_kwargs = {
        "items": filter_name,
        "like": filter_like,
        "regex": filter_regex,
        "invert": filter_invert,
        "intersection": filter_intersection,
    }

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


from .compare import compare
from .conform import conform
from .replace import replace
from .subset import subset

main.add_command(compare)
main.add_command(conform)
main.add_command(replace)
main.add_command(subset)
