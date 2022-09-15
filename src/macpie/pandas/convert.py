import pandas as pd

import macpie.pandas as mppd


def conform(
    left: pd.DataFrame,
    right: pd.DataFrame,
    subset_pair_kwargs={},
    dtypes=False,
    index_order=False,
    values_order=False,
    axis=None,
):
    """
    Conform one Dataframe to another.

    Parameters
    ----------
    left : DataFrame
        DataFrame to conform to.
    right : DataFrame
        DataFrame to conform.
    subset_pair_kwargs : dict, optional
        Keyword arguments to pass to underlying :func:`macpie.pandas.subset_pair`
        to pre-filter columns before comparison.
    dtypes : bool, default is False
        Whether ``right`` should be modified to mimic the dtypes of ``left``
    index_order : bool, default is False
        Whether ``right`` should be modified to mimic the index order of ``left``
    values_order : bool, default is False
        Whether both DataFrames should be sorted by their common labels.
    axis : {0 or `index`, 1 or `columns`, None}, default None
        The axis to conform on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.

    Returns
    -------
    Tuple[DataFrame, DataFrame]
        ``left`` and ``right`` conformed to each other.
    """
    if axis is None:
        axis = left._info_axis_name

    if subset_pair_kwargs:
        (left, right) = mppd.subset_pair(left, right, axis=axis, **subset_pair_kwargs)

    if dtypes:
        right = mimic_dtypes(left, right)

    if index_order:
        right = mimic_index_order(left, right, axis=axis)

    if values_order:
        values_order_axis = "index" if left._get_axis_name(axis) == "columns" else "columns"
        (left, right) = sort_values_pair(left, right, axis=values_order_axis, ignore_index=True)

    return (left, right)


def mimic_dtypes(left: pd.DataFrame, right: pd.DataFrame, categorical=True):
    """
    Cast column data types in ``right`` to be the same as those in ``left``
    where the column name is the same.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    categorical : bool, default is True
        Whether to also ensure categorial data type internals are the same.

    Returns
    -------
    DataFrame
        The modified ``right`` DataFrame
    """

    ((common_columns, _), _) = mppd.filter_labels_pair(
        left, right, intersection=True, axis="columns"
    )

    for col in common_columns:
        if right[col].dtype != left[col].dtype:
            right[col] = right[col].astype(left[col].dtypes.name)
            if categorical and pd.core.dtypes.common.is_categorical_dtype(left[col]):
                right[col] = right[col].astype(
                    pd.api.types.CategoricalDtype(
                        categories=left[col].cat.categories, ordered=left[col].cat.ordered
                    )
                )

    return right


def mimic_index_order(left: pd.DataFrame, right: pd.DataFrame, axis=None):
    """
    Order the ``right`` labels as close as possible to the order of the ``left`` labels.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    axis : {0 or `index`, 1 or `columns`, None}, default None
        The axis to mimic on, expressed either as an index (int)
        or axis name (str). By default this is the info axis,
        'index' for Series, 'columns' for DataFrame.

    Returns
    -------
    DataFrame
        The modified ``right`` DataFrame
    """
    if axis is None:
        axis = left._info_axis_name

    ((left_labels_returned, _), (_, right_labels_discarded)) = mppd.filter_labels_pair(
        left, right, intersection=True, axis=axis
    )
    common_labels = left_labels_returned
    right_labels_reordered = common_labels + right_labels_discarded
    if right._get_axis(axis).to_list() != right_labels_reordered:
        right = right.reindex(right_labels_reordered, axis=axis)

    return right


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


def to_datetime(df: pd.DataFrame, date_col_name, **kwargs):
    """
    Convert ``date_col_name`` column in ``df`` to datetime.

    Parameters
    ----------
    df : DataFrame
    date_col_name : str
        Column to convert, case-insensitive
    **kwargs
        All keyword arguments are passed through to the underlying
        :func:`pandas.to_datetime` function.

    Returns
    -------
    str
        Properly-cased date column name.
    """
    _date_col = mppd.get_col_name(df, date_col_name)
    if not mppd.is_date_col(df, _date_col):
        df[_date_col] = pd.to_datetime(df[_date_col], **kwargs)
    return _date_col
