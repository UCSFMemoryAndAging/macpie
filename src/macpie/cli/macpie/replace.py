import pathlib
import re

import click
import openpyxl as pyxl
from pandas.core.dtypes.common import is_re_compilable
from tabulate import tabulate

from macpie import openpyxltools, pathtools
from macpie.cli.core import pass_results_resource


@click.command()
@click.option("-r", "--to-replace", required=True)
@click.option("-v", "--value", required=True)
@click.option("--ignorecase", is_flag=True)
@click.option("--regex", is_flag=True)
@click.option("--re-multiline", is_flag=True)
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@pass_results_resource
def replace(results_resource, to_replace, value, ignorecase, regex, re_multiline, files):
    valid_files, invalid_files = pathtools.validate_paths(files, allowed_path)

    for f in invalid_files:
        click.echo(f"WARNING: Ignoring invalid file: {f}")

    if len(valid_files) < 1:
        raise click.UsageError("ERROR: No valid files.")

    results_dir = results_resource.create_results_dir()

    flags = 0
    if regex:
        if not is_re_compilable(to_replace):
            raise TypeError("Could not compile 'to_replace' to regex.")
        if re_multiline:
            flags |= re.MULTILINE

    for file_path in valid_files:
        output_filepath = results_dir / file_path.name

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


def allowed_path(p):
    stem = p.stem
    if stem.startswith("~"):
        return False
    if pathtools.has_excel_extension(p):
        return True
    return False
