import pandas as pd

from macpie._config import get_option
from macpie.tools import validator as validatortools


def group_by_keep_one(
    df: pd.DataFrame,
    group_by_col: str,
    date_col: str,
    keep: str = 'all',
    id_col: str = None,
    drop_duplicates: bool = False
) -> pd.DataFrame:
    """
    Given a :class:`pandas.DataFrame` object, group on the ``group_by_col`` column
    and keep only the earliest or latest row in each group as determined by the date
    in the ``date_col`` column.

    :param df: the DataFrame to operate on
    :param group_by_col: the DataFrame column to group on
    :param date_col: the date column to determine which row is earliest or latest
    :param keep: specify which row of each group to keep

        ``all``
             keep all rows

        ``earliest``
             in each group, keep only the earliest (i.e. oldest) row

        ``latest``
             in each group, keep only the latest (i.e. most recent) row

    :param id_col: if ``drop_duplicates=True``, the column specified
                   here will also be used for identifying duplicates
    :param drop_duplicates: if ``True``, then if more than one row is determined to be
                            earliest or or latest in each group, drop all duplicates
                            except the first occurrence. If ``id_col`` is specified,
                            then that column will also be used for identifying duplicates
    """

    # groupby.first() and groupby.last() can't handle NaN values (ongoing bug)
    # use groupby.nth(0) and groupby.nth(-1) instead

    group_by_col = df.mac.get_col_name(group_by_col)

    date_col = df.mac.to_datetime(date_col)

    if keep not in ['all', 'earliest', 'latest']:
        raise ValueError("invalid keep option")

    id_col = df.mac.get_col_name(id_col) if id_col is not None else None

    drop_duplicates = validatortools.validate_bool_kwarg(drop_duplicates, "drop_duplicates")

    cols = [group_by_col, date_col]

    # first drop rows where group_by col or date col is na and re-index
    df = df.dropna(subset=cols).reset_index(drop=True)

    df = df.sort_values(
        by=cols + [id_col] if id_col is not None else cols,
        na_position='last'
    )

    if keep in {'earliest', 'latest'}:
        pre_results = None

        if keep == 'earliest':
            pre_results = df.groupby(group_by_col, sort=False, as_index=False).nth(0)
        else:
            # keep == 'latest'
            pre_results = df.groupby(group_by_col, sort=False, as_index=False).nth(-1)

        # in case there are duplicates, keep them

        pre_results = pre_results.filter(items=cols)
        df = pd.merge(
            df,
            pre_results,
            how='inner',
            on=cols,
            indicator=False
        )

    dup_cols = cols + [id_col] if id_col is not None else cols
    dups = df.duplicated(subset=dup_cols, keep=False)
    if dups.any():
        if drop_duplicates:
            df = df.drop_duplicates(subset=dup_cols, keep='first', ignore_index=True)
        else:
            df.mac.insert(get_option("column.system.duplicates"), dups)

    return df
