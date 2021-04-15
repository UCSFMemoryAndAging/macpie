from macpie import pandas
from macpie._config import get_option
from macpie.core.dataset import Dataset


def date_proximity(
    left: Dataset,
    right: Dataset,
    get: str = 'all',
    when: str = 'earlier_or_later',
    days: int = 90,
    dropna: bool = False,
    drop_duplicates: bool = False,
    duplicates_indicator: bool = False,
    merge_suffixes=get_option("operators.binary.column_suffixes")
) -> None:
    """

    """
    result_df = pandas.operators.date_proximity.date_proximity(
        left.df,
        right.df,
        id_left_on=left.id2_col,
        id_right_on=right.id2_col,
        date_left_on=left.date_col,
        date_right_on=right.date_col,
        get=get,
        when=when,
        days=days,
        left_link_id=left.id_col,
        dropna=dropna,
        drop_duplicates=drop_duplicates,
        duplicates_indicator=duplicates_indicator,
        merge='partial',
        merge_suffixes=merge_suffixes
    )

    right.set_df(result_df)
