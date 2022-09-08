import pathlib
from collections import namedtuple

import click

import macpie as mp
from macpie.cli.core import ResultsResource

possible_engines = ["pandas", "tablib"]


FilePairSheetPairs = namedtuple("FilePairSheetPairs", ["file_pair", "sheet_pairs"])


@click.group(chain=True)
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-s", "--sheet", multiple=True)
@click.option("-p", "--sheet-pair", nargs=2, multiple=True)
@click.argument(
    "files",
    nargs=2,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, path_type=pathlib.Path
    ),
)
@click.pass_context
def main(ctx, verbose, sheet, sheet_pair, files):
    """This script processes a pair of files. One command feeds into the next."""


@main.result_callback()
@click.pass_context
def process_commands(ctx, processors, verbose, sheet, sheet_pair, files):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    rr = ResultsResource(ctx=ctx, verbose=verbose)
    rr.create_results_dir()
    ctx.obj = ctx.with_resource(rr)

    stream = FilePairSheetPairs(files, process_sheet_options(files, sheet, sheet_pair))

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

main.add_command(compare)
main.add_command(conform)
