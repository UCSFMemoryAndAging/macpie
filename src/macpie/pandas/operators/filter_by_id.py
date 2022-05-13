from typing import List

import pandas as pd


def filter_by_id(df: pd.DataFrame, id_col_name: str, ids: List[int]) -> pd.DataFrame:
    """
    Filters a :class:`pandas.DataFrame` object to only include a specified list
    of numerical IDs in a specified numerical ID column.

    Parameters
    ----------
    df : DataFrame
        To be filtered
    id_col_name : str
        The DataFrame column to filter on
    ids: list
        The list of IDs to filter on in the ``id_col_name`` column

    Returns
    -------
    DataFrame
        A DataFrame of the filtered result.
    """

    try:
        _ids = [int(i) for i in ids]
    except ValueError as error:
        raise ValueError(f"ids list contains an invalid number: {error}")

    _id_col = df.mac.get_col_name(id_col_name)

    return df.loc[df[_id_col].isin(_ids)].reset_index(drop=True)
