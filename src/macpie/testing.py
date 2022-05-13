"""
Public testing utility functions.
"""

import pandas as pd

from macpie import datetimetools


def assert_dfs_equal(
    left: pd.DataFrame,
    right: pd.DataFrame,
    cols_ignore=set(),
    cols_ignore_pat="$^",
    output_dir=None,
):
    """For testing equality of :class:`pandas.DataFrame` objects

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    cols_ignore : list-like, optional
        Columns to ignore
    cols_ignore_pat : Regular expression. Default is ``$^``
        Column names that match will be ignored. Default pattern is ``$^``
        which matches nothing so no columns are ignored.
    output_dir : Path, optional
        Directory to write row difference results to
    """

    if left.mac.equals(right, cols_ignore, cols_ignore_pat):
        return True

    right = left.mac.assimilate(right)

    # check columns
    (left_only_cols, right_only_cols) = left.mac.diff_cols(
        right, cols_ignore=cols_ignore, cols_ignore_pat=cols_ignore_pat
    )

    if left_only_cols != set() or right_only_cols != set():
        assert False, f"\nleft_only_cols: {left_only_cols}\nright_only_cols: {right_only_cols}"

    # check rows
    pd.testing.assert_index_equal(left.index, right.index)

    row_diffs = left.mac.diff_rows(right, cols_ignore=cols_ignore, cols_ignore_pat=cols_ignore_pat)

    if row_diffs.mac.row_count() > 0:
        if output_dir is not None:
            row_diffs_filename = (
                "row_diffs_" + datetimetools.current_datetime_str(ms=True) + ".xlsx"
            )
            row_diffs.to_excel(output_dir / row_diffs_filename, index=False)

        assert False, f"\nrow_diffs: {row_diffs}"


def assert_excels_equal(wb1, wb2):
    """
    For testing equality of :class:`openpyxl.workbook.workbook.Workbook` objects

    Parameters
    ----------
    wb1 : Workbook
        Left Workbook to compare
    wb2 : Workbook
        Right Workbook to compare
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
                assert c1.value == c2.value, f"{sheet}.{c1.coordinate}: {c1.value} != {c2.value}"
