"""
Public testing utility functions.
"""

from macpie.util import append_current_datetime_ms_str


def assert_dfs_equal(df1, df2, cols_ignore=None, output_dir=None):
    df2_assimilated = df1.mac.assimilate(df2)

    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2_assimilated, cols_ignore=cols_ignore)

    assert set() == left_only_cols
    assert set() == right_only_cols

    drows = df1.mac.diff_rows(df2_assimilated, cols_ignore=cols_ignore)

    row_diffs_filename = append_current_datetime_ms_str("row_diffs") + ".xlsx"

    if output_dir is not None:
        drows.to_excel(output_dir / row_diffs_filename, index=False)

    assert drows.mac.num_rows() == 0
