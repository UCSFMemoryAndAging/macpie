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
from macpie.util import Masker, MaskMap

from macpie.cli.core import allowed_path, pass_results_resource

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
DEFAULT_COLS_NO_RENAME = [
    "daydiff",
    "dcstatus",
    "vtype",
]

# Default columns to drop because they contain PHI or unnecessarily risky data
DEFAULT_COLS_TO_DROP = ["ageatdc", "careid", "instrtype"]


def masker_params(func):
    func = click.option(
        "--random-seed",
        type=int,
        default=None,
        help="Random seed used to create masking data.",
    )(func)

    func = click.option(
        "--id-cols",
        multiple=True,
        type=str,
        default=DEFAULT_ID_COLS,
        required=True,
        help="ID columns to mask with first set of replacement IDs.",
    )(func)

    func = click.option(
        "--id-range",
        nargs=2,
        default=DEFAULT_ID_RANGE,
        required=True,
        help="Length-2 tuple specifying range of IDs possible in --id-cols.",
    )(func)

    func = click.option(
        "--date-cols",
        multiple=True,
        type=str,
        default=DEFAULT_DATE_COLS,
        help="Date columns to mask with first set of replacement IDs.",
    )(func)

    func = click.option(
        "--id2-cols",
        multiple=True,
        type=str,
        default=DEFAULT_ID2_COLS,
        help="ID columns to mask with second set of replacement IDs.",
    )(func)

    func = click.option(
        "--id2-range",
        nargs=2,
        type=int,
        default=DEFAULT_ID2_RANGE,
        help="Length-2 tuple specifying range of IDs possible in --id2-cols.",
    )(func)

    func = click.option(
        "--cols-no-rename",
        multiple=True,
        default=DEFAULT_COLS_NO_RENAME,
        help=("Columns not to mask (leave untouched). Other options will override these columns."),
    )(func)

    func = click.option(
        "--cols-to-drop",
        multiple=True,
        default=DEFAULT_COLS_TO_DROP,
        help="Columns to drop (e.g. because they contain PHI or unnecessarily risky data.)",
    )(func)

    func = click.option(
        "--output-id-maps",
        is_flag=True,
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
@pass_results_resource
def masker(
    results_resource,
    input_path,
    random_seed,
    id_cols,
    id_range,
    date_cols,
    id2_range,
    id2_cols,
    cols_no_rename,
    cols_to_drop,
    output_id_maps,
):
    valid_filepaths, invalid_filepaths = mp.pathtools.validate_paths(input_path, allowed_path)

    for i in invalid_filepaths:
        click.echo(f"WARNING: Ignoring invalid file: {i}")

    if len(valid_filepaths) < 1:
        raise click.UsageError("ERROR: No valid files.")

    mask_map_1 = MaskMap.from_id_range(id_range[0], id_range[1], random_seed=random_seed)
    mask_map_2 = MaskMap.from_id_range(
        id2_range[0], id2_range[1], day_shift=False, random_seed=random_seed
    )

    masker = Masker(mask_map_1, id_cols, date_col_names=date_cols)
    masker.add(mask_map_2, id2_cols)

    results_dir = results_resource.create_results_dir()

    for file_path in valid_filepaths:
        click.echo(f"\nProcessing file: {file_path.resolve()}")
        output_filepath = results_dir / file_path.name

        if file_path.suffix == ".csv":
            df = mp.pandas.read_file(file_path)
            try:
                masker.mask_df(
                    df, drop_cols=cols_to_drop, norename_cols=cols_no_rename, inplace=True
                )
                df.to_csv(output_filepath, index=False)
            except Exception as err:
                click.echo(err)
        elif file_path.suffix == ".xlsx":
            with pd.ExcelWriter(output_filepath) as writer:
                sheets_dict = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, sheet_df in sheets_dict.items():
                    click.echo(f"\tProcessing worksheet: {sheet_name}")
                    try:
                        masker.mask_df(
                            sheet_df,
                            drop_cols=cols_to_drop,
                            norename_cols=cols_no_rename,
                            inplace=True,
                        )
                    except Exception as err:
                        click.echo(err)
                    else:
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

    if output_id_maps:
        if id_cols:
            mask_map_1.to_csv_file(results_dir / "mask_map_1.csv")
        if id2_cols:
            mask_map_2.to_csv_file(results_dir / "mask_map_2.csv")
