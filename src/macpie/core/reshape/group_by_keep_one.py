from macpie import pandas
from macpie.core.dataset import Dataset


def group_by_keep_one(
    dset: Dataset,
    keep: str = 'all',
    drop_duplicates: bool = False
) -> None:
    """Given a :class:`Dataset` object, group on the :attr:`Dataset.id2_col` column
    and keep only the earliest or latest row in each group as determined by the date
    in the :attr:`Dataset.date_col` column.

    This is the :class:`Dataset` analog of :func:`macpie.pandas.group_by_keep_one`.

    :param dset: the :class:`Dataset` to operate on. Its ``df`` attribute
                 gets updated with the result of this operation.
    :param keep: specify which row of each group to keep

        ``all``
             keep all rows

        ``earliest``
             in each group, keep only the earliest (i.e. oldest) row

        ``latest``
             in each group, keep only the latest (i.e. most recent) row

    :param drop_duplicates: if ``True``, then if more than one row is determined to be
                            earliest or or latest in each group, drop all duplicates
                            except the first occurrence. ``dset``'s ``id_col`` will
                            be used for identifying duplicates
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
