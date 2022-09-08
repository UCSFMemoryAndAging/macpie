from typing import Optional
import warnings

import pandas as pd

from macpie._config import get_option
from macpie.tools import lltools, validatortools


def date_proximity(
    left,
    right,
    id_on=None,
    id_left_on=None,
    id_right_on=None,
    date_on=None,
    date_left_on=None,
    date_right_on=None,
    get: str = "all",
    when: str = "earlier_or_later",
    days: int = 90,
    left_link_id=None,
    dropna: bool = False,
    drop_duplicates: bool = False,
    duplicates_indicator: bool = False,
    merge="partial",
    merge_suffixes=get_option("operators.binary.column_suffixes"),
    prepend_levels=(None, None),
) -> pd.DataFrame:
    """
    Links data across two :class:`pandas.DataFrame` objects by date proximity.

    Specifically, a "left" DataFrame contains a timepoint anchor, and a "right"
    DataFrame is linked to the left by retrieving all rows that match on a
    specified id col, and whose specified date fields are within a certain
    time range of each other.

    Parameters
    ----------
    left : DataFrame
        Contains the timepoint anchor
    right : DataFrame
        To be linked to ``left``
    id_on: str
        Primary column to join on. These must be found in both DataFrames.
    id_left_on : str
        Primary column to join on in the left DataFrame
    id_right_on: str
        Primary column to join on in the right DataFrame
    date_on : str
        Date columns to use for timepoint matching. These must
        be found in both DataFrames, and the one on the left
        will act as timepoint anchor.
    date_left_on : str
        Date column in left DataFrame to act as timepoint anchor.
    date_right_on: str
        Date column in right DataFrame to compare with left's timepoint anchor
    get : {'all', 'closest'}, default 'all'
        Indicates which rows of the right DataFrame to link in reference to the
        timepoint anchor:

        * all: keep all rows
        * closest: get only the closest row that is within ``days`` days of the
          timepoint anchor
    when : {'earlier', 'later', 'earlier_or_later'}, default 'earlier_or_later'
        Indicates which rows of the right DataFrame to link in temporal relation
        to the timepoint anchor

        * earlier: get only rows that are earlier than the timepoint anchor
        * later: get only rows that are lter (more recent) than the timepoint anchor
        * earlier_or_later: get rows that are earlier or later than the timepoint anchor
    days : int, default 90
        The time range measured in days
    left_link_id : str, optional
        The id column in the left DataFrame to act as the primary key of that
        data. This helps to ensure there are no duplicates in the left
        DataFrame (i.e. rows with the same ``id_left_on`` and ``date_left_on``)
    dropna : bool, default: False
        Whether to exclude rows that did not find any match
    drop_duplicates : bool, default: False
        If ``True``, then if more than one row in the right DataFrame is found,
        all will be dropped except the last one.
    duplicates_indicator : bool or str, default False
        If True, adds a column to the output DataFrame called "_mp_duplicates"
        denoting which rows are duplicates. The column can be given a different
        name by providing a string argument.
    merge : {'partial', 'full'}, default 'partial'
        Indicates which columns to include in result

        * partial: include only columns from the right DataFrame
        * full: include all columns from both left and right DataFrames
    merge_suffixes : list-like, default is ("_x", "_y")
        A length-2 sequence where the first element is suffix to add to the
        left DataFrame columns, and second element is suffix to add to the
        right DataFrame columns.
    prepend_levels : list-like, default is (None, None)
        A length-2 sequence where each element is optionally a string indicating
        a top-level index to add to columnn indexes in ``left`` and ``right``
        respectively (thus creating a :class:`pandas.MultiIndex` if needed).
        Pass a value of ``None`` instead of a string to indicate that the column
        index in ``left`` or ``right`` should be left as-is. At least one of the
        values must not be ``None``.

    Returns
    -------
    DataFrame
        A DataFrame of the two linked objects.
    """

    op = _DateProximityOperation(
        left,
        right,
        id_on=id_on,
        id_left_on=id_left_on,
        id_right_on=id_right_on,
        date_on=date_on,
        date_left_on=date_left_on,
        date_right_on=date_right_on,
        get=get,
        when=when,
        days=days,
        left_link_id=left_link_id,
        dropna=dropna,
        drop_duplicates=drop_duplicates,
        duplicates_indicator=duplicates_indicator,
        merge=merge,
        merge_suffixes=merge_suffixes,
        prepend_levels=prepend_levels,
    )
    return op.get_result()


class _DateProximityOperation:
    def __init__(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        id_on=None,
        id_left_on=None,
        id_right_on=None,
        date_on=None,
        date_left_on=None,
        date_right_on=None,
        get: str = "all",
        when: str = "earlier_or_later",
        days: int = 90,
        left_link_id=None,
        dropna: bool = False,
        drop_duplicates: bool = False,
        duplicates_indicator: bool = False,
        merge="partial",
        merge_suffixes=get_option("operators.binary.column_suffixes"),
        prepend_levels=(None, None),
    ):
        self.left = left
        self.right = right

        self.id_on = lltools.maybe_make_list(id_on)
        self.id_left_on = lltools.maybe_make_list(id_left_on)
        self.id_right_on = lltools.maybe_make_list(id_right_on)

        self.date_on = date_on
        self.date_left_on = date_left_on
        self.date_right_on = date_right_on

        self.get = get
        self.when = when
        self.days = days

        self.left_link_id = left_link_id

        self.dropna = validatortools.validate_bool_kwarg(dropna, "dropna")
        self.drop_duplicates = validatortools.validate_bool_kwarg(
            drop_duplicates, "drop_duplicates"
        )

        self.duplicates_indicator = duplicates_indicator

        self.duplicates_indicator_name: Optional[str]
        if isinstance(self.duplicates_indicator, str):
            self.duplicates_indicator_name = self.duplicates_indicator
        elif isinstance(self.duplicates_indicator, bool):
            self.duplicates_indicator_name = (
                get_option("column.system.duplicates") if self.duplicates_indicator else None
            )
        else:
            raise ValueError("indicator option can only accept boolean or string arguments")

        self.merge = merge
        self.merge_suffixes = merge_suffixes
        self.prepend_levels = prepend_levels

        self._left_suffix = get_option("operators.binary.column_suffixes")[0]
        self._right_suffix = get_option("operators.binary.column_suffixes")[1]
        self._diff_days_col = get_option("column.system.diff_days")
        self._abs_diff_days_col = get_option("column.system.abs_diff_days")
        self._merge_indicator_col = get_option("column.system.merge")

        self._validate_specification()

    def get_result(self):
        result = self._get_all()
        if self.get == "closest":
            result = self._get_closest(result)
        result = self._handle_dropna(result)
        result = self._handle_duplicates(result)
        result = self._handle_merge(result)

        return result

    def _get_all(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Ignore the following warning caused when merging on dataframes
            # with MultiIndex columns:
            # PerformanceWarning: dropping on a non-lexsorted multi-index
            # without a level parameter may impact performance.
            # obj = obj._drop_axis(labels, axis, level=level, errors=errors)

            everything = pd.merge(
                self.link_table,
                self.right,
                how="left",
                left_on=self.id_left_on,
                right_on=self.id_right_on,
                indicator=self._merge_indicator_col,
            )

        # fix the leveling of the merge indicator column created by pd.merge
        if self._right_level:
            everything.rename(
                columns={
                    self._merge_indicator_col: self._right_level,
                    "": self._merge_indicator_col,
                },
                inplace=True,
            )

        # create a column 'diff_days' with date difference in days
        everything = everything.mac.add_diff_days(
            self.date_left_on, self.date_right_on, self._diff_days_col
        )

        # keep rows where the date differences within range
        # create copy to avoid chained indexing and getting a SettingWithCopyWarning
        all_candidates = everything.loc[abs(everything[self._diff_days_col]) <= self.days].copy()

        if self.when == "earlier":
            all_candidates = all_candidates.loc[all_candidates[self._diff_days_col] <= 0]
        elif self.when == "later":
            all_candidates = all_candidates.loc[all_candidates[self._diff_days_col] >= 0]

        return all_candidates

    def _get_closest(self, all_candidates):
        # create a column containing the absolute value of diff_days
        all_candidates.loc[:, self._abs_diff_days_col] = all_candidates[self._diff_days_col].abs()

        all_candidates = all_candidates.sort_values(
            by=self.link_table_cols + [self._abs_diff_days_col],
            # by=['index', self._abs_diff_days_col],
            inplace=False,
            na_position="last",
        )

        groupby_cols = self.id_left_on + [self.date_left_on]

        closest_candidates = all_candidates[
            (
                all_candidates[self._abs_diff_days_col]
                == all_candidates.groupby(groupby_cols)[[self._abs_diff_days_col]].transform(
                    "min"
                )[self._abs_diff_days_col]
            )
        ]

        return closest_candidates

    def _handle_dropna(self, result):
        if self.dropna is False:
            left_frame = self.left[self.link_table_cols] if self.merge == "partial" else self.left
            result = pd.merge(
                left_frame, result, how="left", on=self.link_table_cols, indicator=False
            )

        return result

    def _handle_duplicates(self, result):
        dups = result.duplicated(subset=self.link_table_cols, keep=False)

        # handle duplicates
        if dups.any():
            if self.drop_duplicates:
                result = result.drop_duplicates(
                    subset=self.link_table_cols, keep="last", ignore_index=True
                )
            elif self.duplicates_indicator:
                result.mac.insert(self.duplicates_indicator_name, dups)
        return result

    def _handle_merge(self, result):
        left_suffix = self.merge_suffixes[0]
        right_suffix = self.merge_suffixes[1]

        if self.merge == "partial":
            result = result.mac.drop_suffix(self._right_suffix)
            result = result.mac.replace_suffix(self._left_suffix, left_suffix)
        else:
            result = result.mac.replace_suffix(self._left_suffix, left_suffix)
            result = result.mac.replace_suffix(self._right_suffix, right_suffix)

        return result

    def _validate_specification(self):
        if self.id_on:
            if self.id_left_on or self.id_right_on:
                raise ValueError(
                    'Must pass argument "id_on" OR "id_left_on" '
                    'and "id_right_on", but not a combination of both.'
                )
            self.id_left_on = self.left.mac.get_col_names(self.id_on)
            self.id_right_on = self.right.mac.get_col_names(self.id_on)
        elif self.id_left_on and self.id_right_on:
            if len(self.id_left_on) != len(self.id_right_on):
                raise ValueError("len(id_right_on) must equal len(id_left_on)")
            self.id_left_on = self.left.mac.get_col_names(self.id_left_on)
            self.id_right_on = self.right.mac.get_col_names(self.id_right_on)
        else:
            raise ValueError(
                'Must pass argument "id_on" OR "id_left_on" '
                'and "id_right_on", but not a combination of both.'
            )

        if not self.date_on:
            if not self.date_left_on or not self.date_right_on:
                raise ValueError(
                    'Must pass argument "date_on" OR "date_left_on" '
                    'and "date_right_on", but not a combination of both.'
                )
            self.date_left_on = self.left.mac.get_col_name(self.date_left_on)
            self.date_right_on = self.right.mac.get_col_name(self.date_right_on)
        else:
            if self.date_left_on or self.date_right_on:
                raise ValueError(
                    'Must pass argument "date_on" OR "date_left_on" '
                    'and "date_right_on", but not a combination of both.'
                )
            self.date_left_on = self.date_right_on = self.left.mac.get_col_name(self.date_on)

        self.date_left_on = self.left.mac.get_col_name(self.date_left_on)
        self.date_right_on = self.right.mac.get_col_name(self.date_right_on)

        if not self.left.mac.is_date_col(self.date_left_on):
            self.left.mac.to_datetime(self.date_left_on)
            # raise TypeError(
            #    f"'date_left_on' column of '{self.date_left_on}' is not a valid date column"
            # )

        if not self.right.mac.is_date_col(self.date_right_on):
            self.right.mac.to_datetime(self.date_right_on)
            # raise TypeError(
            #    f"'date_right_on' column of '{self.date_right_on}' is not a valid date column"
            # )

        if self.get not in ["all", "closest"]:
            raise ValueError(f"invalid get option: {self.get}")

        if self.when not in ["earlier", "later", "earlier_or_later"]:
            raise ValueError(f"invalid when option: {self.when}")

        if isinstance(self.days, int):
            if self.days < 0:
                raise ValueError("days option value cannot be negative")
        else:
            raise TypeError("days option needs to be an integer")

        # check for duplicates
        if not self.left_link_id:
            has_dupes = self.left[self.id_left_on + [self.date_left_on]].duplicated().any()
            if has_dupes:
                raise ValueError(
                    f"Duplicate rows with the same '{self.id_left_on}' and '{self.date_left_on}' exist. Aborting."
                )
        else:
            self.left_link_id = self.left.mac.get_col_name(self.left_link_id)
            has_dupes = self.left[self.left_link_id].duplicated().any()
            if has_dupes:
                raise ValueError(
                    f"ID column '{self.left_link_id}' must be unique but is not. Aborting."
                )

        if self.merge not in ["partial", "full"]:
            raise ValueError(f"invalid merge option: {self.merge}")

        if not lltools.is_list_like(self.merge_suffixes):
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )
        elif len(self.merge_suffixes) != 2:
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )

        self._add_suffixes()

        if not lltools.is_list_like(self.prepend_levels):
            raise ValueError(
                "'prepend_levels' needs to be a tuple or list of two values "
                "(e.g. ('left','right') or (None,'right'))"
            )
        elif len(self.prepend_levels) != 2:
            raise ValueError(
                "'prepend_levels' needs to be a tuple or list of two values "
                "(e.g. ('left','right') or (None,'right'))"
            )

        self._left_level = self.prepend_levels[0]
        self._right_level = self.prepend_levels[1]

        if self._left_level:
            self.left = self.left.mac.prepend_multi_index_level(self._left_level, axis=1)
            self.id_left_on = [(self._left_level, id_left_on) for id_left_on in self.id_left_on]
            self.date_left_on = (self._left_level, self.date_left_on)
            if self.left_link_id:
                self.left_link_id = (self._left_level, self.left_link_id)
        if self._right_level:
            self.right = self.right.mac.prepend_multi_index_level(self._right_level, axis=1)
            self.id_right_on = [
                (self._right_level, id_right_on) for id_right_on in self.id_right_on
            ]
            self.date_right_on = (self._right_level, self.date_right_on)
            self._diff_days_col = (self._right_level, self._diff_days_col)
            self._abs_diff_days_col = (self._right_level, self._abs_diff_days_col)

        self._create_link_helpers()

    def _add_suffixes(self):
        self.left = self.left.add_suffix(self._left_suffix)
        self.right = self.right.add_suffix(self._right_suffix)
        self.id_left_on = [id_col_name + self._left_suffix for id_col_name in self.id_left_on]
        self.id_right_on = [id_col_name + self._right_suffix for id_col_name in self.id_right_on]
        self.date_left_on = self.date_left_on + self._left_suffix
        self.date_right_on = self.date_right_on + self._right_suffix

        if self.left_link_id:
            self.left_link_id = self.left_link_id + self._left_suffix

    def _create_link_helpers(self):
        link_table_cols = []
        link_table_cols.extend(self.id_left_on)
        link_table_cols.append(self.date_left_on)
        if self.left_link_id:
            link_table_cols.append(self.left_link_id)

        self.link_table_cols = link_table_cols
        self.link_table = self.left[link_table_cols]


def merge(
    left,
    right,
    on=None,
    left_on=None,
    right_on=None,
    merge_suffixes=get_option("operators.binary.column_suffixes"),
    add_suffixes=False,
    add_indexes=(None, None),
) -> pd.DataFrame:
    """
    Merge :class:`pandas.DataFrame` objects with a database-style join, similar to
    :meth:`pandas.DataFrame.merge`, but with additional options.

    Parameters
    ----------
    left : DataFrame
    right : DataFrame
    on : label or list
        See :meth:`pandas.DataFrame.merge`
    left_on : label or list, or array-like
        See :meth:`pandas.DataFrame.merge`
    right_on : label or list, or array-like
        See :meth:`pandas.DataFrame.merge`
    merge_suffixes :
        See :meth:`pandas.DataFrame.merge`, ``suffixes`` parameter.
        Only added if ``add_suffixes`` is ``True``.
    add_suffixes : bool, default False
        Whether to add the suffixes specified in ``merge_suffixes`` or not
    add_indexes : list-like, default is (None, None)
        A length-2 sequence where each element is optionally a string
        indicating a top-level index to add to columnn indexes in ``left``
        and ``right`` respectively (thus creating a :class:`pandas.MultiIndex`
        if needed). Pass a value of ``None`` instead of a string
        to indicate that the column index in ``left`` or ``right`` should be
        left as-is. At least one of the values must not be ``None``.

    Returns
    -------
    DataFrame
        A DataFrame of the result.
    """

    op = _MergeOperation(
        left,
        right,
        on=on,
        left_on=left_on,
        right_on=right_on,
        merge_suffixes=merge_suffixes,
        add_suffixes=add_suffixes,
        add_indexes=add_indexes,
    )
    return op.get_result()


class _MergeOperation:

    _left_suffix = None
    _right_suffix = None

    _left_superindex = None
    _right_superindex = None

    def __init__(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        on=None,
        left_on=None,
        right_on=None,
        merge_suffixes=get_option("operators.binary.column_suffixes"),
        add_suffixes=False,
        add_indexes=(None, None),
    ):

        self.left = self.orig_left = left
        self.right = self.orig_right = right

        self.on = lltools.maybe_make_list(on)
        self.left_on = lltools.maybe_make_list(left_on)
        self.right_on = lltools.maybe_make_list(right_on)

        self.merge_suffixes = merge_suffixes

        self.add_suffixes = validatortools.validate_bool_kwarg(add_suffixes, "add_suffixes")

        self.add_indexes = add_indexes

        self._validate_specification()

    def get_result(self):
        if self.add_suffixes:
            self._add_suffixes()

        if self._left_superindex:
            self.left.columns = pd.MultiIndex.from_product(
                [[self._left_superindex], self.left.columns]
            )

        if self._right_superindex:
            self.right.columns = pd.MultiIndex.from_product(
                [[self._right_superindex], self.right.columns]
            )

        result = pd.merge(
            self.left,
            self.right,
            how="left",
            left_on=[(self._left_superindex, col) for col in self.left_on]
            if self._left_superindex
            else self.left_on,
            right_on=[(self._right_superindex, col) for col in self.right_on]
            if self._right_superindex
            else self.right_on,
            suffixes=self.merge_suffixes,
        )

        return result

    def _validate_specification(self):
        if self.on:
            if self.left_on or self.right_on:
                raise ValueError(
                    'Must pass argument "on" OR "left_on" '
                    'and "right_on", but not a combination of both.'
                )
            self.left_on = self.left.mac.get_col_names(self.on)
            self.right_on = self.right.mac.get_col_names(self.on)
        elif self.left_on and self.right_on:
            if len(self.left_on) != len(self.right_on):
                raise ValueError("len(right_on) must equal len(left_on)")
            self.left_on = self.left.mac.get_col_names(self.left_on)
            self.right_on = self.right.mac.get_col_names(self.right_on)
        else:
            raise ValueError(
                'Must pass argument "on" OR "left_on" '
                'and "right_on", but not a combination of both.'
            )

        if not lltools.is_list_like(self.merge_suffixes):
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )
        elif len(self.merge_suffixes) != 2:
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )

        self._left_suffix = self.merge_suffixes[0]
        self._right_suffix = self.merge_suffixes[1]

        if not lltools.is_list_like(self.add_indexes):
            raise ValueError(
                "'add_indexes' needs to be a tuple or list of two values (e.g. ('left','right') or (None,'right'))"
            )
        elif len(self.add_indexes) != 2:
            raise ValueError(
                "'add_indexes' needs to be a tuple or list of two values (e.g. ('left','right') or (None,'right'))"
            )

        self._left_superindex = self.add_indexes[0]
        self._right_superindex = self.add_indexes[1]

    def _add_suffixes(self):
        if self._left_suffix:
            self.left = self.left.add_suffix(self._left_suffix)
            self.left_on = [col + self._left_suffix for col in self.left_on]

        if self._right_suffix:
            self.right = self.right.add_suffix(self._right_suffix)
            self.right_on = [col + self._right_suffix for col in self.right_on]
