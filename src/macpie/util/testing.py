"""
Public testing utility functions.
"""

from pandas.testing import assert_index_equal

from . import datetime


def assert_dfs_equal(df1, df2, cols_ignore=None, output_dir=None):
    """
    For testing equality of :class:`pandas.DataFrame` objects

    :param df1: left DataFrame to compare
    :param df2: right DataFrame to compare
    :param cols_ignore: DataFrame columns to ignore in comparison
    :param output_dir: directory to write row difference results to
    """
    df2_assimilated = df1.mac.assimilate(df2)

    # check columns
    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2_assimilated, cols_ignore=cols_ignore)

    assert set() == left_only_cols
    assert set() == right_only_cols

    # check rows
    assert_index_equal(df1.index, df2_assimilated.index)

    drows = df1.mac.diff_rows(df2_assimilated, cols_ignore=cols_ignore)

    row_diffs_filename = datetime.append_current_datetime_ms_str("row_diffs") + ".xlsx"

    if output_dir is not None:
        drows.to_excel(output_dir / row_diffs_filename, index=False)

    assert drows.mac.num_rows() == 0


def assert_excels_equal(wb1, wb2):
    """
    For testing equality of :class:`openpyxl.workbook.workbook.Workbook` objects

    :param wb1: left Workbook to compare
    :param wb2: right Workbook to compare
    """
    # same sheets?
    assert set(wb1.sheetnames) == set(wb2.sheetnames)

    # each sheet has same range of data?
    for sheet in wb1.sheetnames:
        assert wb1[sheet].max_column == wb2[sheet].max_column
        assert wb1[sheet].max_row == wb2[sheet].max_row

    # each sheet has same data in each cell?
    for sheet in wb1.sheetnames:
        ws1 = wb1[sheet]
        ws2 = wb2[sheet]
        for x in range(1, ws1.max_row + 1):
            for y in range(1, ws1.max_column + 1):
                c1 = ws1.cell(row=x, column=y)
                c2 = ws2.cell(row=x, column=y)
                assert c1.value == c2.value, \
                    f'{sheet}.{c1.coordinate}: {c1.value} != {c2.value}'
