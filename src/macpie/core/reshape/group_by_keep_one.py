from macpie import pandas
from macpie.core.dataset import Dataset


def group_by_keep_one(
    dset: Dataset,
    keep: str = 'all',
    drop_duplicates: bool = False
) -> None:
    """

    """
    result_df = pandas.operators.group_by_keep_one.group_by_keep_one(
        df=dset.df,
        group_by_col=dset.id2_col,
        date_col=dset.date_col,
        keep=keep,
        id_col=dset.id_col,
        drop_duplicates=drop_duplicates
    )

    dset.df = result_df
