import pandas as pd

from macpie.util import validate_bool_kwarg


def group_by_keep_one(
    df: pd.DataFrame,
    group_by_col: str,
    date_col: str,
    keep: str = 'all',
    id_col: str = None,
    drop_duplicates: bool = False
) -> pd.DataFrame:
    # groupby.first() and groupby.last() can't handle NaN values (ongoing bug)
    # use groupby.nth(0) and groupby.nth(-1) instead

    _group_by_col = df.mac.get_col_name(group_by_col)

    _date_col = df.mac.to_datetime(date_col)

    if keep not in ['all', 'first', 'latest']:
        raise ValueError("invalid keep option")

    _keep = keep

    _id_col = df.mac.get_col_name(id_col) if id_col is not None else None

    _drop_duplicates = validate_bool_kwarg(drop_duplicates, "drop_duplicates")

    _cols = [_group_by_col, _date_col]

    # first drop rows where group_by col or date col is na and re-index
    _df = df.dropna(subset=_cols).reset_index(drop=True)

    _df = _df.sort_values(
        by=_cols + [_id_col] if _id_col is not None else _cols,
        na_position='last'
    )

    if _keep in {'first', 'latest'}:
        pre_results = None

        if _keep == 'first':
            pre_results = _df.groupby(_group_by_col, sort=False, as_index=False).nth(0)
        else:
            # keep == 'latest'
            pre_results = _df.groupby(_group_by_col, sort=False, as_index=False).nth(-1)

        # in case there are duplicates, keep them

        pre_results = pre_results.filter(items=_cols)
        _df = pd.merge(
            _df,
            pre_results,
            how='inner',
            on=_cols,
            indicator=False
        )

    if _drop_duplicates:
        _df = _df.drop_duplicates(
            subset=_cols + [_id_col] if _id_col is not None else _cols,
            keep='first',
            ignore_index=True
        )

    return _df
