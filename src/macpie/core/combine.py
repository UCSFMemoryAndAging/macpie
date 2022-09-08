from macpie._config import get_option
from macpie.core.dataset import Dataset


def date_proximity(
    left: Dataset,
    right: Dataset,
    get: str = "all",
    when: str = "earlier_or_later",
    days: int = 90,
    dropna: bool = False,
    drop_duplicates: bool = False,
    duplicates_indicator: bool = False,
    merge_suffixes=get_option("operators.binary.column_suffixes"),
    prepend_level_name: bool = True,
) -> None:
    """Links data across two :class:`Dataset` objects by date proximity,
    first joining them on their :attr:`Dataset.id2_col_name`.

    Specifically, a `left` Dataset contains a timepoint anchor, and a `right`
    Dataset is linked to the `left` by retrieving all rows that match on
    :attr:`Dataset.id2_col_name`, and whose :attr:`Dataset.date_col_name`
    fields are within a certain time range of each other.

    This is the :class:`Dataset` analog of :func:`macpie.pandas.date_proximity`.


    Parameters
    ----------
    left : Dataset
        Contains the timepoint anchor (i.e. `date_col`)
    right : Dataset
        The Dataset to link.
    get : {'all', 'closest'}, default 'all'
        Indicates which rows of the right Dataset to link in reference to the
        timepoint anchor:

        * all: keep all rows
        * closest: get only the closest row that is within ``days`` days of the
          timepoint anchor
    when : {'earlier', 'later', 'earlier_or_later'}, default 'earlier_or_later'
        Indicates which rows of the right Dataset to link in temporal relation
        to the timepoint anchor

        * earlier: get only rows that are earlier than the timepoint anchor
        * later: get only rows that are lter (more recent) than the timepoint anchor
        * earlier_or_later: get rows that are earlier or later than the timepoint anchor
    days : int, default 90
        The time range measured in days
    dropna : bool, default: False
        Whether to exclude rows that did not find any match
    drop_duplicates : bool, default: False
        If ``True``, then if more than one row in the right DataFrame is found,
        all will be dropped except the last one.
    duplicates_indicator : bool or str, default False
        If True, adds a column to the output DataFrame called "_mp_duplicates"
        denoting which rows are duplicates. The column can be given a different
        name by providing a string argument.
    merge_suffixes : list-like, default is ("_x", "_y")
        A length-2 sequence where the first element is suffix to add to the
        left DataFrame columns, and second element is suffix to add to the
        right DataFrame columns.
    prepend_levels : bool, default True
        Whether to add a top-level index using the :attr:`Dataset.name` attribute
        to column indexes in ``left`` and ``right`` respectively (thus
        creating a :class:`pandas.MultiIndex` if needed).
    """

    if prepend_level_name:
        prepend_levels = (left.name, right.name)
    else:
        prepend_levels = (None, None)

    from macpie.pandas.combine import date_proximity

    result_df = date_proximity(
        left,
        right,
        id_left_on=left.id2_col_name,
        id_right_on=right.id2_col_name,
        date_left_on=left.date_col_name,
        date_right_on=right.date_col_name,
        get=get,
        when=when,
        days=days,
        left_link_id=left.id_col_name,
        dropna=dropna,
        drop_duplicates=drop_duplicates,
        duplicates_indicator=duplicates_indicator,
        merge="partial",
        merge_suffixes=merge_suffixes,
        prepend_levels=prepend_levels,
    )

    if prepend_level_name:
        new_id_col_name = (right.name, right.id_col_name)
        new_date_col_name = (right.name, right.date_col_name)
        new_id2_col_name = (right.name, right.id2_col_name)
    else:
        new_id_col_name = right.id_col_name
        new_date_col_name = right.date_col_name
        new_id2_col_name = right.id2_col_name

    return Dataset(
        result_df,
        id_col_name=new_id_col_name,
        date_col_name=new_date_col_name,
        id2_col_name=new_id2_col_name,
        name=right.name,
    )

    # right.set_df(result_df)
