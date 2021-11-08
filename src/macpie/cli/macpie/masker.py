"""
Command to mask (i.e. de-identify) data contained in your files, specifically
PHI data contained in ID and Date columns. In the MAC Lava database, for
example, these would be any columns containing PIDNs, InstrIDs, and Dates of Service
(e.g. DCDate, VDate).

This command accepts comma separated value files (.csv) as well as Excel
(.xlsx) files. If an Excel file is included, all worksheets in the Excel file
will be masked.

USAGE
=====

You can specify which ID columns to mask in DEFAULT_ID_COLS, or via the command
line using the --id-col option. If you use the --id-col option,
all defaults will be overridden.

You can specify which Date columns to mask in DEFAULT_DATE_COLS, or via the command
line using the --date-col option. If you use the --date-col option,
all defaults will be overridden.

You can specify which ID2 columns to mask in DEFAULT_ID2_COLS, or via the command
line using the --id2-col option. If you use the --id2-col option,
all defaults will be overridden.

The last argument(s) is the list of files and/or directories. If a directory is listed,
all .csv and .xlsx files inside the directory will be included in the execution.

Resulting files will be in a results folder created in the current directory.

Examples:

> macpie masker a_single_file.csv

> macpie masker a_single_file.csv another_file.xlsx

> macpie masker folder_containing_multiple_files

> macpie masker --id-col pidn --id-col pidn_link --date-col dcdate --id2-col instrid faq_all.csv

> macpie masker --random-seed 12345 --output-id-maps tests/util/masker/masker_test.xlsx
"""
import pathlib

import click
import pandas as pd

import macpie as mp
from macpie import pathtools
from macpie.util import IdMapCols, Masker

from macpie.cli.common import allowed_path, show_parameter_source

# Note that pseudo-random number generation always produces the same output
# given the same seed. So if the same seed and ID ranges are used, you should
# reliably get the same masking. This is useful if you want to use the same masking
# across multiple executions of the command, which is often the case.
RANDOM_SEED = None

# Default ID columns to mask with one set of replacement IDs
DEFAULT_ID_COLS = ["pidn", "pidn_link"]
DEFAULT_ID_RANGE = (1, 999999)  # upper range not included

# Default Date columns to mask using the day-shift value
# of the first set of replacement IDs (above)
DEFAULT_DATE_COLS = ["dcdate", "dcdate_link", "link_date"]

# Default ID2 columns to mask with a second set of replacement IDs
DEFAULT_ID2_COLS = ["instrid", "instrid_link", "link_id"]
DEFAULT_ID2_RANGE = (1, 999999)  # upper range not included

# Default columns not to mask (leave untouched), UNLESS they are
# directly specified in the above defaults or by the user to mask.
DEFAULT_COLS_NO_MASK = [
    "daydiff",
    "dcdate",
    "dcdate_link",
    "dcstatus",
    "instrid",
    "instrid_link",
    "link_date",
    "link_id",
    "pidn",
    "pidn_link",
    "vtype",
]

# Default columns to drop because they contain PHI or unnecessarily
# risky data
DEFAULT_COLS_TO_DROP = ["ageatdc", "careid", "instrtype"]


def masker_params(func):
    func = click.option(
        "--random-seed",
        type=int,
        envvar="MACPIE_MASKER_RANDOM_SEED",
        default=None,
        callback=show_parameter_source,
        help="Random seed used to create masking data.",
    )(func)

    func = click.option(
        "--id-cols",
        multiple=True,
        type=str,
        envvar="MACPIE_MASKER_ID_COLS",
        default=DEFAULT_ID_COLS,
        required=True,
        callback=show_parameter_source,
        help="ID columns to mask with first set of replacement IDs.",
    )(func)

    func = click.option(
        "--id-range",
        nargs=2,
        type=int,
        envvar="MACPIE_MASKER_ID_RANGE",
        default=DEFAULT_ID_RANGE,
        required=True,
        callback=show_parameter_source,
        help="Length-2 tuple specifying range of IDs possible in --id-cols.",
    )(func)

    func = click.option(
        "--date-cols",
        multiple=True,
        type=str,
        envvar="MACPIE_MASKER_DATE_COLS",
        default=DEFAULT_DATE_COLS,
        callback=show_parameter_source,
        help="Date columns to mask with first set of replacement IDs.",
    )(func)

    func = click.option(
        "--id2-cols",
        multiple=True,
        type=str,
        envvar="MACPIE_MASKER_ID2_COLS",
        default=DEFAULT_ID2_COLS,
        callback=show_parameter_source,
        help="ID columns to mask with second set of replacement IDs.",
    )(func)

    func = click.option(
        "--id2-range",
        nargs=2,
        type=int,
        envvar="MACPIE_MASKER_ID2_RANGE",
        default=DEFAULT_ID2_RANGE,
        callback=show_parameter_source,
        help="Length-2 tuple specifying range of IDs possible in --id2-cols.",
    )(func)

    func = click.option(
        "--cols-no-mask",
        multiple=True,
        envvar="MACPIE_MASKER_COLS_NO_MASK",
        default=DEFAULT_COLS_NO_MASK,
        callback=show_parameter_source,
        help=("Columns not to mask (leave untouched). Other options will override these columns."),
    )(func)

    func = click.option(
        "--cols-to-drop",
        multiple=True,
        envvar="MACPIE_MASKER_COLS_TO_DROP",
        default=DEFAULT_COLS_TO_DROP,
        callback=show_parameter_source,
        help="Columns to drop (e.g. because they contain PHI or unnecessarily risky data.)",
    )(func)

    func = click.option(
        "--output-id-maps",
        is_flag=True,
        callback=show_parameter_source,
        help="Whether to output the ID maps to a file for later use.",
    )(func)

    return func


@click.command()
@masker_params
@click.argument(
    "input-path",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@click.pass_context
def masker(
    ctx,
    input_path,
    random_seed,
    id_cols,
    id_range,
    date_cols,
    id2_range,
    id2_cols,
    cols_no_mask,
    cols_to_drop,
    output_id_maps,
):
    command_meta = ctx.obj
    results_dir = pathtools.create_dir_with_datetime(dir_name_prefix="results_")

    valid_filepaths, invalid_filepaths = mp.pathtools.validate_paths(input_path, allowed_path)

    for i in invalid_filepaths:
        click.echo(f"WARNING: Ignoring invalid file: {i}")

    if len(valid_filepaths) < 1:
        raise click.UsageError("ERROR: No valid files.")

    id_map_cols = IdMapCols.from_ids(
        list(range(id_range[0], id_range[1])),
        id_cols,
        date_cols=date_cols,
        random_seed=random_seed,
    )

    id2_map_cols = IdMapCols.from_ids(
        list(range(id2_range[0], id2_range[1])), id2_cols, date_cols=False, random_seed=random_seed
    )

    masker = Masker(
        [id_map_cols, id2_map_cols], cols_to_drop=cols_to_drop, cols_no_mask=cols_no_mask
    )

    for file_path in valid_filepaths:
        click.echo(f"\nProcessing file: {file_path.resolve()}")
        mask_file(masker, file_path, results_dir)

    if output_id_maps:
        if id_cols:
            id_map.to_csv_file(results_dir / "id_map.csv")
        if id2_cols:
            id2_map.to_csv_file(results_dir / "id2_map.csv")


def mask_file(masker, input_filepath, output_dir):
    output_filepath = output_dir / input_filepath.name

    if input_filepath.suffix == ".csv":
        df = mp.pandas.file_to_dataframe(input_filepath)
        try:
            masked_df, _ = masker.mask_df(df)
            masked_df.to_csv(output_filepath, index=False)
        except Exception as err:
            click.echo(err)

    elif input_filepath.suffix == ".xlsx":
        writer = pd.ExcelWriter(output_filepath)
        sheets_dict = pd.read_excel(input_filepath, sheet_name=None)
        for name, sheet in sheets_dict.items():
            click.echo(f"\tProcessing worksheet: {name}")
            try:
                sheet_masked, _ = masker.mask_df(sheet)
                sheet_masked.to_excel(excel_writer=writer, sheet_name=name, index=False)
            except Exception as err:
                click.echo(err)
        writer.save()
