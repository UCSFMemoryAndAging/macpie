import pathlib

import click
import openpyxl as pyxl
import pandas as pd

from pandas.core.dtypes.common import (
    ensure_object,
    ensure_platform_int,
    ensure_str,
    is_bool,
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_datetime64tz_dtype,
    is_dict_like,
    is_dtype_equal,
    is_extension_array_dtype,
    is_float,
    is_list_like,
    is_number,
    is_numeric_dtype,
    is_re_compilable,
    is_scalar,
    is_timedelta64_dtype,
    pandas_dtype,
)

import macpie as mp
from macpie import BasicList, Dataset, MACPieExcelWriter, openpyxltools, pathtools
from macpie._config import get_option
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import get_client_system_info


@click.command()
@click.option("-r", "--to-replace", required=True)
@click.option("-v", "--value", required=True)
@click.option("--regex", is_flag=True)
@click.option("--ignorecase", is_flag=True)
@click.option("--multiline", is_flag=True)
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@pass_results_resource
def replace(results_resource, to_replace, value, regex, ignorecase, multiline, files):
    # validate
    if regex and not is_re_compilable(to_replace):
        raise TypeError("Could not compile 'to_replace' to regex.")

    valid_files, invalid_files = pathtools.validate_paths(files, allowed_path)

    for f in invalid_files:
        click.echo(f"WARNING: Ignoring invalid file: {f}")

    if len(valid_files) < 1:
        raise click.UsageError("ERROR: No valid files.")

    results_dir = results_resource.create_results_dir()

    for file_path in valid_files:
        click.echo(f"\nProcessing file: {file_path.resolve()}.")

        output_filepath = results_dir / file_path.name

        wb = pyxl.load_workbook(file_path)
        for sheet in wb.sheetnames:
            click.echo(f"\tProcessing sheet: {sheet}. Number of replacements: ", nl=False)
            ws = wb[sheet]
            count = openpyxltools.replace(
                ws,
                to_replace=to_replace,
                value=value,
                regex=regex,
                ignorecase=ignorecase,
                multiline=multiline,
            )
            click.echo(f"{count}")
        wb.save(output_filepath)


def allowed_path(p):
    stem = p.stem
    if stem.startswith("~"):
        return False
    if pathtools.has_excel_extension(p):
        return True
    return False
