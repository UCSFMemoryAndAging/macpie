import pandas as pd

from macpie._config import get_option
from macpie.exceptions import MergeError
from macpie.tools import sequence as seqtools
from macpie.tools import validator as validatortools


def merge(
    left,
    right,
    on=None,
    left_on=None,
    right_on=None,
    merge_suffixes=get_option("operators.binary.column_suffixes"),
    add_suffixes=False,
    add_indexes=(None, None)
) -> pd.DataFrame:
    """Merge :class:`pandas.DataFrame` objects with a database-style join, similar to
    :meth:`pandas.DataFrame.merge`.

    :param left: DataFrame
    :param right: the DataFrame to merge with
    :param on: column(s) to join on. These must be found in both
               DataFrames.
    :param left_on: column(s) to join on in the left DataFrame
    :param right_on: column(s) to join on in the right DataFrame
    :param merge_suffixes: A length-2 sequence where the first element is
                           suffix to add to the left DataFrame columns, and
                           second element is suffix to add to the right DataFrame columns.
                           Only added if ``add_suffixes`` is ``True``.
    :param add_suffixes: Whether to add the suffixes specified in ``merge_suffixes`` or not
    :param add_indexes: A length-2 sequence where each element is optionally a string
                        indicating a top-level index to add to columnn indexes in ``left``
                        and ``right`` respectively (thus creating a :class:`pandas.MultiIndex`
                        if needed). Pass a value of ``None`` instead of a string
                        to indicate that the column index in ``left`` or ``right`` should be
                        left as-is. At least one of the values must not be ``None``.
    """

    op = _MergeOperation(
        left,
        right,
        on=on,
        left_on=left_on,
        right_on=right_on,
        merge_suffixes=merge_suffixes,
        add_suffixes=add_suffixes,
        add_indexes=add_indexes
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
        add_indexes=(None, None)
    ):

        self.left = self.orig_left = left
        self.right = self.orig_right = right

        self.on = seqtools.maybe_make_list(on)
        self.left_on = seqtools.maybe_make_list(left_on)
        self.right_on = seqtools.maybe_make_list(right_on)

        self.merge_suffixes = merge_suffixes

        self.add_suffixes = validatortools.validate_bool_kwarg(add_suffixes, "add_suffixes")

        self.add_indexes = add_indexes

        self._validate_specification()

    def get_result(self):
        if self.add_suffixes:
            self._add_suffixes()

        if self._left_superindex:
            self.left.columns = pd.MultiIndex.from_product([[self._left_superindex], self.left.columns])

        if self._right_superindex:
            self.right.columns = pd.MultiIndex.from_product([[self._right_superindex], self.right.columns])

        result = pd.merge(
            self.left,
            self.right,
            how='left',
            left_on=[(self._left_superindex, col) for col in self.left_on]
                if self._left_superindex else self.left_on,
            right_on=[(self._right_superindex, col) for col in self.right_on]
                if self._right_superindex else self.right_on,
            suffixes=self.merge_suffixes
        )

        return result

    def _validate_specification(self):
        if self.on is not None:
            if self.left_on is not None or self.right_on is not None:
                raise MergeError(
                    'Must pass argument "on" OR "left_on" '
                    'and "right_on", but not a combination of both.'
                )
            self.left_on = self.left.mac.get_col_names(self.on)
            self.right_on = self.right.mac.get_col_names(self.on)
        elif self.left_on is not None and self.right_on is not None:
            if len(self.left_on) != len(self.right_on):
                raise ValueError("len(right_on) must equal len(left_on)")
            self.left_on = self.left.mac.get_col_names(self.left_on)
            self.right_on = self.right.mac.get_col_names(self.right_on)
        else:
            raise MergeError(
                'Must pass argument "on" OR "left_on" '
                'and "right_on", but not a combination of both.'
            )

        if not seqtools.is_list_like(self.merge_suffixes):
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )
        elif len(self.merge_suffixes) != 2:
            raise ValueError(
                "'merge_suffixes' needs to be a tuple or list of two strings (e.g. ('_x','_y'))"
            )

        self._left_suffix = self.merge_suffixes[0]
        self._right_suffix = self.merge_suffixes[1]

        if not seqtools.is_list_like(self.add_indexes):
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
        if self._left_suffix is not None:
            self.left = self.left.add_suffix(self._left_suffix)
            self.left_on = [col + self._left_suffix for col in self.left_on]

        if self._right_suffix is not None:
            self.right = self.right.add_suffix(self._right_suffix)
            self.right_on = [col + self._right_suffix for col in self.right_on]
