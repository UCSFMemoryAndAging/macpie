"""
Public testing utility functions related to pandas.
"""
import pathlib

import pandas as pd

import macpie as mp


def assert_dfs_equal(
    left: pd.DataFrame,
    right: pd.DataFrame,
    filter_kwargs={},
    assimilate=False,
    sort=False,
    compare_kwargs={},
    output_dir=None,
    **kwargs,
):
    """For testing equality of :class:`pandas.DataFrame` objects

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    filter_kwargs : dict, optional
        Keyword arguments to pass to underlying :meth:`macpie.pandas.filter_pair`
        to pre-filter columns before comparing data.
    assimilate : bool, default is False
        Whether to :func:`macpie.pandas.assimilate` the ``right`` into ``left``
        before comparing data.
    sort : bool, default is False
        Whether to :func:`macpie.pandas.imitate_sort` both DataFrames before
        comparing data.
    compare_kwargs : dict, optional
        Keyword arguments to pass to the underling :meth:`macpie.pandas.compare`
    output_dir : Path, optional
        Directory to write col or row difference results to
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`pandas.testing.assert_frame_equal` function.
    """
    if filter_kwargs:
        (left, right) = mp.pandas.filter_pair(left, right, **filter_kwargs)

    if assimilate:
        right = left.mac.assimilate(right)

    if sort:
        (left, right) = mp.pandas.imitate_sort(
            left, right, left_kwargs={"ignore_index": True}, right_kwargs={"ignore_index": True}
        )

    diffs = left.mac.compare(right, **compare_kwargs)
    if not diffs.empty:
        if isinstance(output_dir, pathlib.PurePath):
            output_dir.mkdir(parents=True, exist_ok=True)
            diffs_filename = "diffs_" + mp.datetimetools.current_datetime_str(ms=True) + ".xlsx"
            diffs.to_excel(output_dir / diffs_filename, index=True)
        assert False, f"\ndiffs: {diffs}"

    pd.testing.assert_frame_equal(left, right, **kwargs)
