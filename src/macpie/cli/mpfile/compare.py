import collections
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

    click.secho(
        "Results for comparing as pandas dataframes will be in blue.", bg="blue", fg="white"
    )
    click.echo()
    click.secho(
        "Results for comparing as tablib datasets will be in blue.", bg="green", fg="black"
    )
    click.echo()
    click.echo()

    dfs_results = compare_as_dataframes(file1, file2)
    tlsets_results = compare_as_tablib_datasets(file1, file2)

    with mp.MACPieExcelWriter(results_path) as writer:
        for sheetname, df in dfs_results.items():
            df.to_excel(writer, sheet_name="df_" + sheetname)
        for sheetname, tlset in tlsets_results.items():
            tlset.title = "tl_" + sheetname
            tlset.to_excel(writer)

    click.echo(f"\nResults output to: {results_path.resolve()}\n")


def compare_as_dataframes(file1, file2):
    dfs1_dict = mp.read_excel(file1, sheet_name=None)
    dfs2_dict = mp.read_excel(file2, sheet_name=None)

    dfs_results = collections.OrderedDict()

    for sheet in dfs1_dict:
        if sheet in dfs2_dict:
            df1 = dfs1_dict[sheet]
            df2 = dfs2_dict[sheet]
            try:
                diffs = df1.compare(df2)
                if diffs.empty:
                    click.secho(f"{sheet}: No differences!\n", bg="blue", fg="white")
                else:
                    click.secho(f"{sheet}: Differences found:", bg="blue", fg="white")
                    click.echo(tabulate.tabulate(diffs, headers="keys", tablefmt="grid"))
                    click.echo()
                    dfs_results[sheet] = diffs

            except ValueError:
                # if dfs don't have identical labels or shape

                # first compare columns
                (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2)
                if left_only_cols != set() or right_only_cols != set():
                    if left_only_cols != set():
                        click.secho(
                            f"{sheet}: The following columns exist only in '{file1.stem}'",
                            bg="blue",
                            fg="white",
                        )
                        click.echo(left_only_cols)
                        click.echo()

                    if right_only_cols != set():
                        click.secho(
                            f"{sheet}: The following columns exist only in '{file2.stem}'",
                            bg="blue",
                            fg="white",
                        )
                        click.echo(right_only_cols)
                        click.echo()

                # then compare rows
                else:
                    row_diffs = df1.mac.diff_rows(df2)
                    if row_diffs.empty:
                        click.secho(f"{sheet}: No differences!\n", bg="blue", fg="white")
                    else:
                        click.secho(f"{sheet}: Differences found:", bg="blue", fg="white")
                        click.echo(tabulate.tabulate(row_diffs, headers="keys", tablefmt="grid"))
                        click.echo()
                        dfs_results[sheet] = row_diffs

    return dfs_results


def compare_as_tablib_datasets(file1, file2):
    with mp.MACPieExcelFile(file1) as reader:
        tlsets1_dict = reader.parse_simple_datasets(sheet_name=None)

    with mp.MACPieExcelFile(file2) as reader:
        tlsets2_dict = reader.parse_simple_datasets(sheet_name=None)

    tlsets_results = collections.OrderedDict()

    for sheet in tlsets1_dict:
        if sheet in tlsets2_dict:
            tlset1 = tlsets1_dict[sheet]
            tlset2 = tlsets2_dict[sheet]
            try:
                diffs = tlset1.compare(tlset2)

                if diffs.height == 0:
                    click.secho(f"{sheet}: No differences!\n", bg="green", fg="black")
                else:
                    click.secho(f"{sheet}: Differences found:", bg="green", fg="black")
                    click.echo(tabulate.tabulate(diffs, headers="keys", tablefmt="grid"))
                    click.echo()
                    tlsets_results[sheet] = diffs
            except ValueError:
                click.echo("Couldn't compare: datasets don't have matching labels or shape.")

    return tlsets_results
