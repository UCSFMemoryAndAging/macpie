import macpie as mp


def group_by_keep_one(dset: mp.Dataset, keep: str = "all", drop_duplicates: bool = False) -> None:
    """Given a :class:`Dataset` object, group on the :attr:`Dataset.id2_col_name` column
    and keep only the earliest or latest row in each group as determined by the date
    in the :attr:`Dataset.date_col_name` column.

    This is the :class:`Dataset` analog of :func:`macpie.pandas.group_by_keep_one`.

    Parameters
    ----------
    dset : Dataset
    keep: {'all', 'earliest', 'latest'}, default 'all'
        Specify which row of each group to keep.

        * all: keep all rows
        * earliest: in each group, keep only the earliest (i.e. oldest) row
        * latest: in each group, keep only the latest (i.e. most recent) row
    drop_duplicates : bool, default: False
        If ``True``, then if more than one row is determined to be
        'earliest' or 'latest' in each group, drop all duplicates
        except the first occurrence. If ``dset`` has an ``id_col_name``,
        then that column will also be used for identifying duplicates
    """
    result_df = mp.pandas.operators.group_by_keep_one.group_by_keep_one(
        df=dset,
        group_by_col=dset.id2_col_name,
        date_col_name=dset.date_col_name,
        keep=keep,
        id_col_name=dset.id_col_name,
        drop_duplicates=drop_duplicates,
    )

    return mp.Dataset(data=result_df)
    # dset.df = result_df
