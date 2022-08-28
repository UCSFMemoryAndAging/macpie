"""
Public testing utility functions related to pandas.
"""

import pandas as pd

import macpie.datetimetools
import macpie.openpyxltools


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
                "row_diffs_" + macpie.datetimetools.current_datetime_str(ms=True) + ".xlsx"
            )
            row_diffs.to_excel(output_dir / row_diffs_filename, index=False)

        assert False, f"\nrow_diffs: {row_diffs}"
