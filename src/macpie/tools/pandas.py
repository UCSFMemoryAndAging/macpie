from typing import Optional, Sequence, Union

import pandas as pd


def is_potential_multi_index(
    columns, index_col: Optional[Union[bool, Sequence[int]]] = None
):
    """Check whether or not the `columns` parameter
    could be converted into a MultiIndex.

    :param columns: Object which may or may not be convertible into a MultiIndex
    :param index_col: Column or columns to use as the (possibly hierarchical) index

    :return: Whether or not columns could become a MultiIndex
    """
    if index_col is None or isinstance(index_col, bool):
        index_col = []

    return (
        len(columns)
        and not isinstance(columns, pd.MultiIndex)
        and all(isinstance(c, tuple) for c in columns if c not in list(index_col))
    )


def maybe_make_multi_index_columns(self, columns, col_names=None):
    """possibly create a column mi here

    :param columns: Object which may or may not be made into a MultiIndex
    :param col_names: Names for the levels in the index
    """
    # possibly create a column mi here
    if is_potential_multi_index(columns):
        columns = pd.MultiIndex.from_tuples(columns, names=col_names)
    return columns
