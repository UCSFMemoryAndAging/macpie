import pandas as pd

from macpie.util import is_list_like, maybe_make_list
from macpie.exceptions import DateProximityError
from macpie.util import validate_bool_kwarg


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
    merge='partial',
    merge_suffixes=('_x', '_y')
) -> pd.DataFrame:
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
        merge=merge,
        merge_suffixes=merge_suffixes
    )
    return op.get_result()


class _DateProximityOperation:

    _left_suffix = "_x"
    _right_suffix = "_y"

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
        merge='partial',
        merge_suffixes=("_x", "_y")
    ):
        self.left = self.orig_left = left
        self.right = self.orig_right = right

        self.id_on = maybe_make_list(id_on)
        self.id_left_on = maybe_make_list(id_left_on)
        self.id_right_on = maybe_make_list(id_right_on)

        self.date_on = date_on
        self.date_left_on = date_left_on
        self.date_right_on = date_right_on

        self.get = get
        self.when = when
        self.days = days

        self.left_link_id = left_link_id

        self.dropna = validate_bool_kwarg(dropna, "dropna")

        self.merge = merge
        self.merge_suffixes = merge_suffixes

        self._validate_specification()

        self._add_suffixes()

        link_table_cols = self.id_left_on.copy()
        link_table_cols.append(self.date_left_on)
        if self.left_link_id is not None:
            link_table_cols.append(self.left_link_id)

        self.link_table_cols = link_table_cols
        self.link_table = self.left[link_table_cols]

    def get_result(self):
        # print()
        # print(self.left)
        # print(self.right)
        # print(self.link_table)

        result = self._get_all()

        # print(result)

        if self.get == 'closest':
            result = self._get_closest(result)
            # print(result)

        result = self._format_result(result)

        # print(result)

        return result

    def _get_all(self):
        everything = pd.merge(
            self.link_table,
            self.right,
            how='left',
            left_on=self.id_left_on,
            right_on=self.id_right_on,
            indicator=True
        )

        # create a column 'diff_days' with date difference in days
        everything = everything.mac.add_diff_days(
            self.date_left_on,
            self.date_right_on
        )

        # keep rows where the date differences within range
        # create copy to avoid chained indexing and getting a SettingWithCopyWarning
        all_candidates = everything.loc[abs(everything['_diff_days']) <= self.days].copy()

        if self.when == 'earlier':
            all_candidates = all_candidates.loc[all_candidates['_diff_days'] <= 0]
        elif self.when == 'later':
            all_candidates = all_candidates.loc[all_candidates['_diff_days'] >= 0]

        return all_candidates

    def _get_closest(self, all_candidates):
        # create a column containing the absoluate value of diff_days
        all_candidates.loc[:, '_abs_diff_days'] = all_candidates['_diff_days'].abs()

        all_candidates = all_candidates.sort_values(
            by=self.link_table_cols + ['_abs_diff_days'],
            # by=['index', '_abs_diff_days'],
            inplace=False,
            na_position='last'
        )

        groupby_cols = self.id_left_on + [self.date_left_on]
        closest_candidates = all_candidates[
            (all_candidates['_abs_diff_days']
             == all_candidates.groupby(groupby_cols)['_abs_diff_days'].transform('min'))
        ]

        return closest_candidates

    def _format_result(self, result):

        left_suffix = self.merge_suffixes[0]
        right_suffix = self.merge_suffixes[1]

        final = result

        if self.dropna is False:
            left_frame = self.left[self.link_table_cols] if self.merge == 'partial' else self.left
            final = pd.merge(
                left_frame,
                final,
                how='left',
                on=self.link_table_cols,
                indicator=False
            )

        final = final.mac.mark_duplicates_by_cols(self.link_table_cols)

        if self.merge == 'partial':
            final = final.mac.drop_suffix(self._right_suffix)
            final = final.mac.replace_suffix(self._left_suffix, '_link')
        else:
            final = final.mac.replace_suffix(self._left_suffix, left_suffix)
            final = final.mac.replace_suffix(self._right_suffix, right_suffix)

        return final

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

        if not is_list_like(self.merge_suffixes):
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )
        elif len(self.merge_suffixes) != 2:
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )

    def _add_suffixes(self):
        self.left = self.left.add_suffix(self._left_suffix)
        self.right = self.right.add_suffix(self._right_suffix)
        self.id_left_on = [id_col + self._left_suffix for id_col in self.id_left_on]
        self.id_right_on = [id_col + self._right_suffix for id_col in self.id_right_on]
        self.date_left_on = self.date_left_on + self._left_suffix
        self.date_right_on = self.date_right_on + self._right_suffix

        if self.left_link_id is not None:
            self.left_link_id = self.left_link_id + self._left_suffix
