from typing import Optional, Sequence, Union

import pandas as pd

from macpie.tools import strtools


def drop_suffix(df: pd.DataFrame, suffix):
    """
    Removes the ``suffix`` in any column name containing the ``suffix``.

    Parameters
    ----------
    df : DataFrame
    suffix : str
        suffix to drop

    Returns
    -------
    DataFrame
        DataFrame with renamed columns.
    """

    return df.rename(columns=lambda x: strtools.strip_suffix(x, suffix))


def flatten_multiindex(df: pd.DataFrame, axis: int = 0, delimiter: str = "_"):
    """
    Flatten (i.e. collapse) the multiindex on a particular ``axis`` using
    a ``delimiter``.

    Parameters
    ----------
    df : DataFrame
    axis : {0 or 'index', 1 or 'columns'}, default 0
        Whether to flatten labels from the index (0 or 'index') or
        columns (1 or 'columns').
    delimiter : str, default is "_"
        String to join multiindex levels on

    Examples
    --------
    Basic usage

    >>> df = pd.DataFrame({"PIDN": [1, 2], "InstrID": [3, 4]})
    >>> df.columns = pd.MultiIndex.from_product([["CDR"], df.columns])
    >>> df
       CDR
      PIDN InstrID
    0    1       3
    1    2       4

    >>> df.mac.flatten_multiindex(axis=1)
    >>> df
       CDR_PIDN  CDR_InstrID
    0         1            3
    1         2            4
    """

    axis_name = df._get_axis_name(axis)
    if axis_name == "index":
        if isinstance(df.index, pd.MultiIndex):
            df.index = [delimiter.join(str(idx) for idx in idx_tup) for idx_tup in df.index]
    elif axis_name == "columns":
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [delimiter.join(str(col) for col in col_tup) for col_tup in df.columns]


def insert(df: pd.DataFrame, col_name, col_value, **kwargs):
    """
    Adds a column to the end of the DataFrame

    Parameters
    ----------
    df : DataFrame
    col_name : str
        Name of column to insert
    col_value : str
        Value of column to insert
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :meth:`pandas.DataFrame.insert` method.
    """
    return df.insert(len(df.columns), col_name, col_value, **kwargs)


def is_potential_multi_index(columns, index_col: Optional[Union[bool, Sequence[int]]] = None):
    """
    Check whether or not the `columns` parameter could be converted into a MultiIndex.

    Parameters
    ----------
    columns : Object which may or may not be convertible into a MultiIndex
    index_col : Column or columns to use as the (possibly hierarchical) index

    Returns
    -------
    bool
        Whether or not columns could become a MultiIndex
    """

    if index_col is None or isinstance(index_col, bool):
        index_col = []

    return (
        len(columns)
        and not isinstance(columns, pd.MultiIndex)
        and all(isinstance(c, tuple) for c in columns if c not in list(index_col))
    )


def maybe_make_multi_index_columns(columns, col_names=None):
    """
    Possibly create a column mi here

    Parameters
    ----------
    columns : Object which may or may not be made into a MultiIndex
    col_names : Names for the levels in the index

    Returns
    -------
    MultiIndex columns if possible, otherwise original columns.
    """

    # possibly create a column mi here
    if is_potential_multi_index(columns):
        columns = pd.MultiIndex.from_tuples(columns, names=col_names)
    return columns


def prepend_multi_index_level(df: pd.DataFrame, level_name: str, axis: int = 0):
    """
    Prepend a MultiIndex level.
    """

    return pd.concat([df], keys=[level_name], axis=axis)


def replace_suffix(df: pd.DataFrame, old_suffix, new_suffix):
    """
    For any column names containing ``old_suffix``, replace the ``old_suffix``
    with ``new_suffix``.

    Parameters
    ----------
    df : DataFrame
    old_suffix : str
        suffix to replace
    new_suffix : str
        suffix to replace ``old_suffix``
    """
    return df.rename(
        columns=lambda x: x[: -len(old_suffix)] + new_suffix if x.endswith(old_suffix) else x
    )
