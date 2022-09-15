import pandas as pd

import macpie.pandas as mppd


def sort_values_pair(
    left: pd.DataFrame, right: pd.DataFrame, right_only=False, axis="index", **kwargs
):
    """
    Sort the pair of DataFrames using their common labels.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    right_only : bool, default is False
        Whether to only sort the values of ``right``
    axis : {0 or `index`, 1 or `columns`}, default 'index'
        Axis to be sorted.
    **kwargs
        All keyword arguments are passed through to the underlying
        :meth:`pandas.DataFrame.sort_values` method.
    """
    filter_axis = "columns" if axis == "index" else "columns"
    ((common_labels, _), _) = mppd.filter_labels_pair(
        left, right, intersection=True, axis=filter_axis
    )
    if not right_only:
        left = left.sort_values(by=common_labels, axis=axis, **kwargs)
    right = right.sort_values(by=common_labels, axis=axis, **kwargs)

    return (left, right)
