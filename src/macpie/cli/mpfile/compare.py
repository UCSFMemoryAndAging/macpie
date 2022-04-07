import collections
import pathlib

import click
import pandas as pd
import tabulate

import macpie as mp


possible_engines = ["pandas", "tablib"]


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-s", "--sheet", multiple=True)
@click.option("-p", "--sheet-pair", nargs=2, multiple=True)
@click.option("-c", "--sort-col")
@click.option("-e", "--engines", multiple=True, default=possible_engines)
@click.argument(
    "files",
    nargs=2,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, path_type=pathlib.Path
    ),
)
@click.pass_context
def compare(ctx, verbose, sheet, sheet_pair, sort_col, engines, files):
    for engine in engines:
        if engine not in possible_engines:
            raise click.BadOptionUsage(
                "engines", f"Invalid engine: '{engine}'. Possible engines: {possible_engines}", ctx
            )

    left_file, right_file = files
    sheet_pairs = process_sheet_options(left_file, right_file, sheet, sheet_pair)

    click.echo("\nComparing")
    click.secho(f"'{left_file.resolve()}'", bold=True)
    click.echo("to")
    click.secho(f"'{right_file.resolve()}'", bold=True)
    click.echo("using the following pairs of worksheets:")
    click.secho(f"{sheet_pairs}\n\n", bold=True)

    click.secho(
        "Results for comparing as pandas dataframes will be in blue.", bg="blue", fg="white"
    )
    click.echo()
    click.secho(
        "Results for comparing as tablib datasets will be in green.", bg="green", fg="black"
    )
    click.echo("\n")

    results_dir = pathlib.Path(".")
    results_filename = (
        left_file.stem
        + "_"
        + right_file.stem
        + "_diffs_"
        + mp.datetimetools.current_datetime_str()
        + ".xlsx"
    )
    results_path = results_dir / results_filename

    # singleton excel_writer
    class excel_writer:
        instance = None

        def __new__(cls):
            if cls.instance is None:
                cls.instance = mp.MACPieExcelWriter(
                    results_path,
                )
            return cls.instance

    if "pandas" in engines:
        dfs_results = compare_files_as_dataframes(
            left_file, right_file, sheet_pairs, sort_col=sort_col
        )

        for sheetname, df in dfs_results.items():
            click.secho(sheetname, bg="blue", fg="white", bold=True)
            if verbose:
                click.echo(tabulate.tabulate(df, headers="keys", tablefmt="grid"))
            click.echo()

            df.to_excel(excel_writer(), sheet_name=sheetname)

    if "tablib" in engines:
        tlsets_results = compare_files_as_tablib_datasets(
            left_file, right_file, sheet_pairs, sort_col=sort_col
        )

        for sheetname, tlset in tlsets_results.items():
            click.secho(sheetname, bg="green", fg="black", bold=True)
            if verbose:
                click.echo(tabulate.tabulate(tlset, headers=tlset.headers, tablefmt="grid"))
            click.echo()

            tlset.title = sheetname
            tlset.to_excel(excel_writer())

    if excel_writer.instance is None:
        click.echo("No differences found.")
    else:
        excel_writer().close()
        click.secho(f"\nResults output to: {results_path.resolve()}\n", bold=True)


def process_sheet_options(left_file, right_file, sheet, sheet_pair):
    results = []

    if sheet:
        for s in sheet:
            results.append((s, s))

    if sheet_pair:
        for sp in sheet_pair:
            results.append(sp)

    if not results:
        left_sheets = mp.openpyxltools.get_sheet_names(left_file)
        right_sheets = mp.openpyxltools.get_sheet_names(right_file)
        common_sheets = list(set(left_sheets).intersection(right_sheets))
        for cs in common_sheets:
            results.append((cs, cs))
        if not results:
            results.append((left_sheets[0], right_sheets[0]))

    return results


def compare_files_as_dataframes(left_file, right_file, sheet_pairs, sort_col=None):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    left_dfs_dict = pd.read_excel(left_file, sheet_name=left_sheets)
    right_dfs_dict = pd.read_excel(right_file, sheet_name=right_sheets)

    dfs_results = collections.OrderedDict()
    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_df = left_dfs_dict[left_sheetname]
        right_df = right_dfs_dict[right_sheetname]
        result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
            "df" + "|" + left_sheetname + "|" + right_sheetname
        )

        if sort_col:
            try:
                left_df = left_df.sort_values(by=[sort_col], na_position="last", ignore_index=True)
                right_df = right_df.sort_values(
                    by=[sort_col], na_position="last", ignore_index=True
                )
            except KeyError:
                click.secho(
                    f"{result_sheetname}|Warning: No column '{sort_col}'. Cannot sort.",
                    bg="yellow",
                    fg="black",
                )

        comparison_result_df = compare_dataframes(left_df, right_df)

        if comparison_result_df is not None:
            dfs_results[result_sheetname] = comparison_result_df

    return dfs_results


def compare_dataframes(left_df, right_df):
    try:
        diffs = left_df.compare(right_df)
        if diffs.empty:
            return None
        return diffs

    except ValueError:
        # if dfs don't have identical labels or shape

        # first compare columns
        (left_only_cols, right_only_cols) = left_df.mac.diff_cols(right_df)
        if left_only_cols != set() or right_only_cols != set():
            col_diffs = pd.DataFrame()
            if left_only_cols != set():
                col_diffs["Left_Only_Cols"] = list(left_only_cols)
            if right_only_cols != set():
                col_diffs["Right_Only_Cols"] = list(right_only_cols)
            return col_diffs

        # then compare rows
        else:
            row_diffs = left_df.mac.diff_rows(right_df)
            if row_diffs.empty:
                return None
            return row_diffs


def compare_files_as_tablib_datasets(left_file, right_file, sheet_pairs, sort_col=None):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    with mp.MACPieExcelFile(left_file) as reader:
        left_tlsets_dict = reader.parse_simple_datasets(sheet_name=left_sheets)

    with mp.MACPieExcelFile(right_file) as reader:
        right_tlsets_dict = reader.parse_simple_datasets(sheet_name=right_sheets)

    tlsets_results = collections.OrderedDict()
    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_tlset = left_tlsets_dict[left_sheetname]
        right_tlset = right_tlsets_dict[right_sheetname]
        result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
            "tl" + "|" + left_sheetname + "|" + right_sheetname
        )

        if sort_col:
            try:
                left_tlset = mp.tablibtools.TablibDataset.from_tlset(left_tlset.sort(sort_col))
                right_tlset = mp.tablibtools.TablibDataset.from_tlset(right_tlset.sort(sort_col))
            except KeyError:
                click.secho(
                    f"{result_sheetname}|Warning: No column '{sort_col}'. Cannot sort.",
                    bg="yellow",
                    fg="black",
                )

        comparison_result_tlset = compare_tablib_datasets(left_tlset, right_tlset)
        if comparison_result_tlset is not None:
            tlsets_results[result_sheetname] = comparison_result_tlset

    return tlsets_results


def compare_tablib_datasets(left_tlset, right_tlset):
    try:
        return left_tlset.compare(right_tlset)
    except ValueError:
        return None
