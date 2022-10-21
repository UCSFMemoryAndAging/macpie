from collections import namedtuple

import click
import pandas as pd

import macpie as mp

FilePairInfo = namedtuple("FilePairInfo", ["file_pair", "sheet_pairs", "filter_kwargs"])


def echo_command_info(title, file_pair_info: FilePairInfo):
    (left_file, right_file), _, _ = file_pair_info
    click.echo()
    click.secho(title, bold=True, bg="green", fg="black")
    click.secho(f"'{left_file.resolve()}'", bold=True)
    click.echo("and")
    click.secho(f"'{right_file.resolve()}'\n", bold=True)


def iter_df_pairs(left_file, right_file, sheet_pairs):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    left_dfs_dict = pd.read_excel(left_file, sheet_name=left_sheets)
    right_dfs_dict = pd.read_excel(right_file, sheet_name=right_sheets)

    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_df = left_dfs_dict[left_sheetname]
        right_df = right_dfs_dict[right_sheetname]
        yield ((left_df, right_df), (left_sheetname, right_sheetname))


def iter_tl_pairs(left_file, right_file, sheet_pairs):
    left_sheets, right_sheets = map(list, zip(*sheet_pairs))

    with mp.MACPieExcelFile(left_file) as reader:
        left_tlsets_dict = reader.parse_tablib_datasets(sheet_name=left_sheets)

    with mp.MACPieExcelFile(right_file) as reader:
        right_tlsets_dict = reader.parse_tablib_datasets(sheet_name=right_sheets)

    for sheet_pair in sheet_pairs:
        left_sheetname, right_sheetname = sheet_pair
        left_tl = left_tlsets_dict[left_sheetname]
        right_tl = right_tlsets_dict[right_sheetname]
        yield ((left_tl, right_tl), (left_sheetname, right_sheetname))
