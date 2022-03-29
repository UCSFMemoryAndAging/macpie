import pathlib

import click
import tabulate

import macpie as mp


@click.command()
@click.argument(
    "files",
    nargs=2,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, path_type=pathlib.Path
    ),
)
@click.pass_context
def compare(ctx, files):
    file1, file2 = files
    df1 = mp.pandas.excel_to_dataframe(file1)
    df2 = mp.pandas.excel_to_dataframe(file2)

    click.echo("\nComparing")
    click.echo(f"'{file1.resolve()}'")
    click.echo("to")
    click.echo(f"'{file2.resolve()}'\n")

    results_dir = pathlib.Path(".")
    results_filename = (
        file1.stem
        + "_"
        + file2.stem
        + "_diffs_"
        + mp.datetimetools.current_datetime_str()
        + ".xlsx"
    )
    results_path = results_dir / results_filename

    try:
        diffs = df1.compare(df2)
        if diffs.empty:
            click.echo("No differences!")
        else:
            click.echo("Differences found:")
            click.echo(tabulate.tabulate(diffs, headers="keys", tablefmt="grid"))
            diffs.to_excel(results_path)
            click.echo(f"\nResults output to: {results_path.resolve()}\n")

    except ValueError:
        # if dfs don't have identical labels or shape

        # first compare columns
        (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2)
        if left_only_cols != set() or right_only_cols != set():
            if left_only_cols != set():
                click.echo(f"The following columns exist only in '{file1.stem}'")
                click.echo(left_only_cols)

            if right_only_cols != set():
                click.echo(f"The following columns exist only in '{file2.stem}'")
                click.echo(right_only_cols)

        # then compare rows
        else:
            row_diffs = df1.mac.diff_rows(df2)
            if row_diffs.empty:
                click.echo("No differences!")
            else:
                click.echo("Differences found:")
                click.echo(tabulate.tabulate(row_diffs, headers="keys", tablefmt="grid"))
                diffs.to_excel(results_path)
                click.echo(f"\nResults output to: {results_path.resolve()}\n")
