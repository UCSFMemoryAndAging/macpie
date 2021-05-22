from typing import Optional

import pandas as pd

from macpie._config import get_option
from macpie.exceptions import DateProximityError
from macpie.tools import sequence as seqtools
from macpie.tools import validator as validatortools


def date_proximity(
    left,
    right,
    id_on=None,
    id_left_on=None,
    id_right_on=None,
    date_on=None,
    date_left_on=None,
    date_right_on=None,
    get: str = 'all',
    when: str = 'earlier_or_later',
    days: int = 90,
    left_link_id=None,
    dropna: bool = False,
    drop_duplicates: bool = False,
    duplicates_indicator: bool = False,
    merge='partial',
    merge_suffixes=get_option("operators.binary.column_suffixes")
) -> pd.DataFrame:
    """Links data across two :class:`pandas.DataFrame` objects by date proximity.

    Specifically, a "left" DataFrame contains a timepoint anchor, and a "right" DataFrame
    is linked to the left by retrieving all rows that match on a specified id col, and
    whose specified date fields are within a certain time range of each other.

    :param left: the DataFrame containing the timepoint anchor
    :param right: the DataFrame to link
    :param id_on: primary column to join on. These must be found in both
                  DataFrames.
    :param id_left_on: primary column to join on in the left DataFrame
    :param id_right_on: primary column to join on in the right DataFrame
    :param date_on: date columns to use for timepoint matching. These must
                    be found in both DataFrames, and the one on the left
                    will act as timepoint anchor.
    :param date_left_on: date column in left DataFrame to act as timepoint anchor.
    :param date_right_on: date column in the right DataFrame to compare with left's
                          timepoint anchor
    :param get: which rows of the right DataFrame to link in reference to the
                timepoint anchor:

        ``all``
             keep all rows

        ``closest``
             get only the closest row that is within ``days`` days of the
             right DataFrame timepoint anchor

    :param when: which rows of the right DataFrame to link in temporal relation
                 to the timepoint anchor

        ``earlier``
             get only rows that are earlier than the timepoint anchor

        ``later``
             get only rows that are lter (more recent) than the timepoint anchor

        ``earlier_or_later``
             get rows that are earlier or later than the timepoint anchor

    :param days: the time range measured in days
    :param left_link_id: the id column in the left DataFrame to act as the
                         primary key of that data. This helps to ensure there
                         are no duplicates in the left DataFrame (i.e. rows with
                         the same ``id_left_on`` and ``date_left_on``)
    :param dropna: whether to exclude rows that did not find any match
    :param merge: which columns to include in result

        ``partial``
             include only columns from the right DataFrame

        ``full``
             include all columns from both left and right DataFrames

    :param merge_suffixes: A length-2 sequence where the first element is
                           suffix to add to the left DataFrame columns, and
                           second element is suffix to add to the right DataFrame columns.
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
        merge_suffixes=merge_suffixes
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
        get: str = 'all',
        when: str = 'earlier_or_later',
        days: int = 90,
        left_link_id=None,
        dropna: bool = False,
        drop_duplicates: bool = False,
        duplicates_indicator: bool = False,
        merge='partial',
        merge_suffixes=get_option("operators.binary.column_suffixes")
    ):
        self.left = self.orig_left = left
        self.right = self.orig_right = right

        self.id_on = seqtools.maybe_make_list(id_on)
        self.id_left_on = seqtools.maybe_make_list(id_left_on)
        self.id_right_on = seqtools.maybe_make_list(id_right_on)

        self.date_on = date_on
        self.date_left_on = date_left_on
        self.date_right_on = date_right_on

        self.get = get
        self.when = when
        self.days = days

        self.left_link_id = left_link_id

        self.dropna = validatortools.validate_bool_kwarg(dropna, "dropna")
        self.drop_duplicates = validatortools.validate_bool_kwarg(drop_duplicates, "drop_duplicates")

        self.duplicates_indicator = duplicates_indicator

        self.duplicates_indicator_name: Optional[str]
        if isinstance(self.duplicates_indicator, str):
            self.duplicates_indicator_name = self.duplicates_indicator
        elif isinstance(self.duplicates_indicator, bool):
            self.duplicates_indicator_name = (
                get_option("column.system.duplicates") if self.duplicates_indicator
                else None
            )
        else:
            raise ValueError(
                "indicator option can only accept boolean or string arguments"
            )

        self.merge = merge
        self.merge_suffixes = merge_suffixes

        self._left_suffix = get_option("operators.binary.column_suffixes")[0]
        self._right_suffix = get_option("operators.binary.column_suffixes")[1]
        self._diff_days_col = get_option("column.system.diff_days")
        self._abs_diff_days_col = get_option("column.system.abs_diff_days")
        self._merge_indicator_col = get_option("column.system.merge")

        self._validate_specification()

    def get_result(self):
        result = self._get_all()
        if self.get == 'closest':
            result = self._get_closest(result)
        result = self._handle_dropna(result)
        result = self._handle_duplicates(result)
        result = self._handle_merge(result)

        return result

    def _get_all(self):
        everything = pd.merge(
            self.link_table,
            self.right,
            how='left',
            left_on=self.id_left_on,
            right_on=self.id_right_on,
            indicator=self._merge_indicator_col
        )

        # create a column 'diff_days' with date difference in days
        everything = everything.mac.add_diff_days(
            self.date_left_on,
            self.date_right_on
        )

        # keep rows where the date differences within range
        # create copy to avoid chained indexing and getting a SettingWithCopyWarning
        all_candidates = everything.loc[abs(everything[self._diff_days_col]) <= self.days].copy()

        if self.when == 'earlier':
            all_candidates = all_candidates.loc[all_candidates[self._diff_days_col] <= 0]
        elif self.when == 'later':
            all_candidates = all_candidates.loc[all_candidates[self._diff_days_col] >= 0]

        return all_candidates

    def _get_closest(self, all_candidates):
        # create a column containing the absoluate value of diff_days
        all_candidates.loc[:, self._abs_diff_days_col] = all_candidates[self._diff_days_col].abs()

        all_candidates = all_candidates.sort_values(
            by=self.link_table_cols + [self._abs_diff_days_col],
            # by=['index', self._abs_diff_days_col],
            inplace=False,
            na_position='last'
        )

        groupby_cols = self.id_left_on + [self.date_left_on]
        closest_candidates = all_candidates[
            (all_candidates[self._abs_diff_days_col]
             == all_candidates.groupby(groupby_cols)[self._abs_diff_days_col].transform('min'))
        ]

        return closest_candidates

    def _handle_dropna(self, result):
        if self.dropna is False:
            left_frame = self.left[self.link_table_cols] if self.merge == 'partial' else self.left
            result = pd.merge(
                left_frame,
                result,
                how='left',
                on=self.link_table_cols,
                indicator=False
            )

        return result

    def _handle_duplicates(self, result):
        dups = result.duplicated(subset=self.link_table_cols, keep=False)

        # handle duplicates
        if dups.any():
            if self.drop_duplicates:
                result = result.drop_duplicates(subset=self.link_table_cols, keep='last', ignore_index=True)
            elif self.duplicates_indicator:
                result.mac.insert(self.duplicates_indicator_name, dups)
        return result

    def _handle_merge(self, result):
        left_suffix = self.merge_suffixes[0]
        right_suffix = self.merge_suffixes[1]

        if self.merge == 'partial':
            result = result.mac.drop_suffix(self._right_suffix)
            result = result.mac.replace_suffix(self._left_suffix, left_suffix)
        else:
            result = result.mac.replace_suffix(self._left_suffix, left_suffix)
            result = result.mac.replace_suffix(self._right_suffix, right_suffix)

        return result

    def _validate_specification(self):
        if self.id_on is not None:
            if self.id_left_on is not None or self.id_right_on is not None:
                raise DateProximityError(
                    'Must pass argument "id_on" OR "id_left_on" '
                    'and "id_right_on", but not a combination of both.'
                )
            self.id_left_on = self.left.mac.get_col_names(self.id_on)
            self.id_right_on = self.right.mac.get_col_names(self.id_on)
        elif self.id_left_on is not None and self.id_right_on is not None:
            if len(self.id_left_on) != len(self.id_right_on):
                raise ValueError("len(id_right_on) must equal len(id_left_on)")
            self.id_left_on = self.left.mac.get_col_names(self.id_left_on)
            self.id_right_on = self.right.mac.get_col_names(self.id_right_on)
        else:
            raise DateProximityError(
                'Must pass argument "id_on" OR "id_left_on" '
                'and "id_right_on", but not a combination of both.'
            )

        if self.date_on is None:
            if self.date_left_on is None or self.date_right_on is None:
                raise DateProximityError(
                    'Must pass argument "date_on" OR "date_left_on" '
                    'and "date_right_on", but not a combination of both.'
                )
            self.date_left_on = self.left.mac.get_col_name(self.date_left_on)
            self.date_right_on = self.right.mac.get_col_name(self.date_right_on)
        else:
            if self.date_left_on is not None or self.date_right_on is not None:
                raise DateProximityError(
                    'Must pass argument "date_on" OR "date_left_on" '
                    'and "date_right_on", but not a combination of both.'
                )
            self.date_left_on = self.left.mac.get_col_name(self.date_on)
            self.date_right_on = self.right.mac.get_col_name(self.date_on)

        self.date_left_on = self.left.mac.to_datetime(self.date_left_on)
        self.date_right_on = self.right.mac.to_datetime(self.date_right_on)

        if self.get not in ['all', 'closest']:
            raise ValueError(f"invalid get option: {self.get}")

        if self.when not in ['earlier', 'later', 'earlier_or_later']:
            raise ValueError(f"invalid when option: {self.when}")

        if isinstance(self.days, int):
            if self.days < 0:
                raise ValueError("days option value cannot be negative")
        else:
            raise TypeError("days option needs to be an integer")

        # check for duplicates
        if self.left_link_id is None:
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

        if self.merge not in ['partial', 'full']:
            raise ValueError(f"invalid merge option: {self.merge}")

        if not seqtools.is_list_like(self.merge_suffixes):
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )
        elif len(self.merge_suffixes) != 2:
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )

        self._add_suffixes()
        self._create_link_helpers()

    def _add_suffixes(self):
        self.left = self.left.add_suffix(self._left_suffix)
        self.right = self.right.add_suffix(self._right_suffix)
        self.id_left_on = [id_col + self._left_suffix for id_col in self.id_left_on]
        self.id_right_on = [id_col + self._right_suffix for id_col in self.id_right_on]
        self.date_left_on = self.date_left_on + self._left_suffix
        self.date_right_on = self.date_right_on + self._right_suffix

        if self.left_link_id is not None:
            self.left_link_id = self.left_link_id + self._left_suffix

    def _create_link_helpers(self):
        link_table_cols = self.id_left_on.copy()
        link_table_cols.append(self.date_left_on)
        if self.left_link_id is not None:
            link_table_cols.append(self.left_link_id)

        self.link_table_cols = link_table_cols
        self.link_table = self.left[link_table_cols]
