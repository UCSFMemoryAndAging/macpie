import collections

import click
import tabulate

import macpie as mp
from macpie.cli.core import pass_results_resource
from macpie.cli.helpers import pipeline_processor, SingletonExcelWriter

from .helpers import echo_command_info, iter_df_pairs, iter_tl_pairs


POSSIBLE_ENGINES = ["pandas", "tablib"]


@click.command()
@click.option("-e", "--engines", multiple=True, default=POSSIBLE_ENGINES)
@pipeline_processor
@pass_results_resource
def compare(results_resource, file_pair_info, engines):
    """Compare a pair of files and output the differences.

    Example:
    \b
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

    echo_command_info("Comparing", file_pair_info)

    results_filename = (
        left_file.stem
        + "_"
        + right_file.stem
        + "_diffs_"
        + mp.datetimetools.current_datetime_str()
        + ".xlsx"
    )

    results_path = results_resource.results_dir / results_filename

    with SingletonExcelWriter(results_path) as writer:

        if "pandas" in engines:
            click.echo("Begin comparing using 'pandas' engine.")
            dfs_results = collections.OrderedDict()
            for (left_df, right_df), (left_sheetname, right_sheetname) in iter_df_pairs(
                left_file, right_file, sheet_pairs
            ):
                click.echo(f"\tComparing '{left_sheetname}' with '{right_sheetname}'... ", nl="")
                diffs_df = left_df.mac.compare(right_df, subset_pair_kwargs=filter_kwargs)
                if not diffs_df.empty:
                    result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
                        "df" + "|" + left_sheetname + "|" + right_sheetname
                    )
                    dfs_results[result_sheetname] = diffs_df
                    click.echo(f"Differences found. See worksheet '{result_sheetname}'")
                else:
                    click.echo("No differences found.")

            for sheetname, df in dfs_results.items():
                if results_resource.verbose:
                    click.echo_via_pager(
                        [sheetname, "\n\n", tabulate.tabulate(df, headers="keys", tablefmt="grid")]
                    )
                df.to_excel(writer(), sheet_name=sheetname)
            if dfs_results:
                click.echo()

        if "tablib" in engines:
            click.echo("Begin comparing using 'tablib' engine.")
            tlsets_results = collections.OrderedDict()
            for (left_tl, right_tl), (left_sheetname, right_sheetname) in iter_tl_pairs(
                left_file, right_file, sheet_pairs
            ):
                click.echo(f"\tComparing '{left_sheetname}' with '{right_sheetname}'... ", nl="")
                (left_tl, right_tl) = mp.tablibtools.subset_pair(
                    left_tl, right_tl, **filter_kwargs
                )
                try:
                    diffs_tl = left_tl.compare(right_tl)
                except ValueError:
                    click.secho(
                        f"Warning: Skipping due to mismatching headers or rows.",
                        fg="yellow",
                    )
                    continue

                if diffs_tl is not None:
                    result_sheetname = mp.io.excel.safe_xlsx_sheet_title(
                        "tl" + "|" + left_sheetname + "|" + right_sheetname
                    )
                    tlsets_results[result_sheetname] = diffs_tl
                    click.echo(f"Differences found. See worksheet '{result_sheetname}'")
                else:
                    click.echo("No differences found.")

            for sheetname, tlset in tlsets_results.items():
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

        click.secho("\nComparison results:", bold=True)
        if writer.instance is None:
            click.echo("No differences found.")
        else:
            click.echo(f"See {results_path.resolve()}")

    # as this command doesn't modify the input files, return original inputs
    return file_pair_info
