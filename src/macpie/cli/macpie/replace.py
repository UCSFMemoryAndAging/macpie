import pathlib
import re

import click
import openpyxl as pyxl
from pandas.core.dtypes.common import is_re_compilable
from tabulate import tabulate

from macpie.cli.core import pass_results_resource
from macpie.tools import openpyxltools, pathtools


def replace_params(func):
    func = click.option("-r", "--to-replace", required=True)(func)
    func = click.option("-v", "--value", required=True)(func)
    func = click.option("--ignorecase", is_flag=True)(func)
    func = click.option("--regex", is_flag=True)(func)
    func = click.option("--re-dotall", is_flag=True)(func)
    return func


@click.command()
@replace_params
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@pass_results_resource
def replace(results_resource, to_replace, value, ignorecase, regex, re_dotall, files):
    valid_files, invalid_files = pathtools.validate_paths(files, allowed_path)

    for f in invalid_files:
        click.echo(f"WARNING: Ignoring invalid file: {f}")

    if len(valid_files) < 1:
        raise click.UsageError("ERROR: No valid files.")

    results_resource.create_results_dir()

    replace_in_files(
        results_resource, valid_files, to_replace, value, ignorecase, regex, re_dotall
    )


def replace_in_files(results_resource, files, to_replace, value, ignorecase, regex, re_dotall):
    flags = 0
    if regex:
        if not is_re_compilable(to_replace):
            raise TypeError("Could not compile 'to_replace' to regex.")
        if re_dotall:
            flags |= re.DOTALL

    result_filepaths = []
    for file_path in files:
        output_filepath = results_resource.results_dir / file_path.name

        wb = pyxl.load_workbook(file_path)
        for sheet in wb.sheetnames:
            click.secho(f"\nProcessing: {file_path.resolve()} - {sheet}", fg="green")

            ws = wb[sheet]
            counter = openpyxltools.replace(
                ws,
                to_replace=to_replace,
                value=value,
                ignorecase=ignorecase,
                regex=regex,
                flags=flags,
            )

            if counter:
                freq = counter.most_common()
                freq.append(("Total", sum(counter.values())))
                click.echo(tabulate(freq, headers=["Replaced", "Count"], tablefmt="pretty"))
            else:
                click.echo("NO REPLACEMENTS")

        wb.save(output_filepath)
        result_filepaths.append(output_filepath)

    return result_filepaths


def allowed_path(p):
    stem = p.stem
    if stem.startswith("~"):
        return False
    if pathtools.has_excel_extension(p):
        return True
    return False
