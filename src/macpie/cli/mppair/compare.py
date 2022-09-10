import collections

import click
import tabulate

import macpie as mp
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor, SingletonExcelWriter

from .main import iter_df_pairs, iter_tl_pairs


POSSIBLE_ENGINES = ["pandas", "tablib"]


@click.command()
@click.option("-e", "--engines", multiple=True, default=POSSIBLE_ENGINES)
@pipeline_processor
@pass_results_resource
def compare(results_resource, file_pair_info, engines):
    """Compare a pair of files and output the differences.

    Examples
    --------
    mppair -i col1 -i col2 file1.xlsx file2.xlsx compare
    """
    for engine in engines:
        if engine not in POSSIBLE_ENGINES:
            raise click.BadOptionUsage(
                "engines",
                f"Invalid engine: '{engine}'. Possible engines: {POSSIBLE_ENGINES}",
                results_resource.ctx,
            )

    (left_file, right_file), sheet_pairs, filter_kwargs = file_pair_info

    click.echo("\nComparing\n")
    click.secho(f"'{left_file.resolve()}'", bold=True)
    click.echo("to")
    click.secho(f"'{right_file.resolve()}'\n", bold=True)
    click.echo("using the following pairs of worksheets:\n")
    click.secho(f"{sheet_pairs}\n\n", bold=True)

    results_filename = (
        left_file.stem
        + "_"
        + right_file.stem
        + "_diffs_"
        + mp.datetimetools.current_datetime_str()
        + ".xlsx"
    )

    results_dir_name = results_resource.create_results_name()
    results_path = results_resource.output_dir / results_dir_name / results_filename

    with SingletonExcelWriter(results_path) as writer:

        if "pandas" in engines:
            dfs_results = collections.OrderedDict()
            for (left_df, right_df), (left_sheetname, right_sheetname) in iter_df_pairs(
                left_file, right_file, sheet_pairs, filter_kwargs=filter_kwargs
            ):
                diffs_df = left_df.mac.compare(right_df)
                if not diffs_df.empty:
                    result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
                        "df" + "|" + left_sheetname + "|" + right_sheetname
                    )
                    dfs_results[result_sheetname] = diffs_df

            if dfs_results:
                click.echo(
                    "Differences found using the 'pandas' engine. See the following worksheets in results file:"
                )
            for sheetname, df in dfs_results.items():
                click.echo(f'\t"{sheetname}"')
                if results_resource.verbose:
                    click.echo_via_pager(
                        [sheetname, "\n\n", tabulate.tabulate(df, headers="keys", tablefmt="grid")]
                    )
                df.to_excel(writer(), sheet_name=sheetname)
            if dfs_results:
                click.echo()

        if "tablib" in engines:
            tlsets_results = collections.OrderedDict()
            for (left_tl, right_tl), (left_sheetname, right_sheetname) in iter_tl_pairs(
                left_file, right_file, sheet_pairs, filter_kwargs=filter_kwargs
            ):

                diffs_tl = left_tl.compare(right_tl)
                if diffs_tl is not None:
                    result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
                        "tl" + "|" + left_sheetname + "|" + right_sheetname
                    )
                    tlsets_results[result_sheetname] = diffs_tl

            if tlsets_results:
                click.echo(
                    "Differences found using the 'tablib' engine. See the following worksheets in results file:"
                )
            for sheetname, tlset in tlsets_results.items():
                click.echo(f'\t"{sheetname}"')
                if results_resource.verbose:
                    click.echo_via_pager(
                        [
                            sheetname,
                            "\n\n",
                            tabulate.tabulate(tlset, headers=tlset.headers, tablefmt="grid"),
                        ]
                    )
                tlset.title = sheetname
                tlset.to_excel(writer())
            if tlsets_results:
                click.echo()

        if writer.instance is None:
            click.echo("No differences found.")
        else:
            results_resource.results_file = results_path

    return file_pair_info
