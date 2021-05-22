from typing import List

import pandas as pd


def filter_by_id(
    df: pd.DataFrame,
    id_col: str,
    ids: List[int]
) -> pd.DataFrame:
    """Filters a :class:`pandas.DataFrame` object to only include a specified list
    of numerical IDs in a specified numerical ID column.

    :param df: the DataFrame to filter
    :param id_col: the DataFrame column to filter on
    :param ids: the list of IDs to filter on in the ``id_col`` column
    """
    try:
        _ids = [int(i) for i in ids]
    except ValueError as error:
        raise ValueError(f"ids list contains an invalid number: {error}")

    _id_col = df.mac.get_col_name(id_col)

    return df.loc[df[_id_col].isin(_ids)].reset_index(drop=True)
