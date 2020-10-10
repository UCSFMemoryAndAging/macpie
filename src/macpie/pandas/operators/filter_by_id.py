from typing import List

import pandas as pd


def filter_by_id(
    df: pd.DataFrame,
    id_col: str,
    ids: List[int]
) -> pd.DataFrame:

    try:
        _ids = [int(i) for i in ids]
    except ValueError as error:
        raise ValueError(f"ids list contains an invalid number: {error}")

    _id_col = df.mac.get_col_name(id_col)

    return df.loc[df[_id_col].isin(_ids)].reset_index(drop=True)
