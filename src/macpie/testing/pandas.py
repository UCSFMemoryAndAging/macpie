"""
Public testing utility functions related to pandas.
"""

from macpie.testing.util import DebugDir
from macpie.tools import datetimetools


def compare_helper(left, right, output_dir=None, **kwargs):
    """Helper for comparing :class:`pandas.DataFrame` objects.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    output_dir : Path, optional
        Directory to write col or row difference results to
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`macpie.pandas.compare` function.
    """
    diffs = left.mac.compare(right, **kwargs)
    if not diffs.empty:
        if output_dir:
            with DebugDir(output_dir):
                diffs_filename = "diffs_" + datetimetools.current_datetime_str(ms=True) + ".xlsx"
                diffs.to_excel(output_dir / diffs_filename, index=True)
        assert False, f"\ndiffs: {diffs}"
