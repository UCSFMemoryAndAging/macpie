from typing import List

import pandas as pd

from macpie import errors
from macpie.core import DataObject
from macpie.pandas import MacDataFrameAccessor


def root_merge(
    root: DataObject,
    leaves: List[DataObject],
) -> pd.DataFrame:
    """
    Merge :class:`macpie.core.DataObject` objects with a database-style join, similar to
    :meth:`pandas.DataFrame.merge`.

    :param root: DataObject
    :param leaves: list of DataObject

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

    op = _RootMergeOperation(
        root,
        leaves
    )
    return op.get_result()


class _RootMergeOperation:

    def __init__(
        self,
        root: DataObject,
        leaves: List[DataObject]
    ):

        self.root = root
        self.leaves = leaves

        self._validate_specification()

    def get_result(self):
        no_duplicates = []
        duplicates = []

        for leaf in self.leaves:
            leaf.df['_duplicates'] = leaf.df.duplicated(subset=leaf.id_col, keep=False)
            if leaf.df['_duplicates'].any():
                duplicates.append(leaf)
            else:
                leaf.df = leaf.df.drop(columns=['_duplicates'])
                no_duplicates.append(leaf)

        merged_name = self.root.name
        merged_df = self.root.df
        merged_df.columns = pd.MultiIndex.from_product([[self.root.name], merged_df.columns])

        for do in no_duplicates:
            merged_df = merged_df.mac.merge(
                do.df,
                left_on=[(self.root.name, self.root.id_col)],
                right_on=[do.id_col],
                add_indexes=(None, do.name)
            )
            merged_name = merged_name + '_' + do.name

        merged_df = merged_df.sort_values(by=[(self.root.name, self.root.id_col)])
        
        merged_do = DataObject(merged_name, merged_df, id_col=(self.root.name, self.root.id_col))

        return (merged_do, duplicates)

    def _validate_specification(self):
        # TODO: already checked in DataObject constructor
        if self.root.df[self.root.id_col].duplicated().any():
            raise errors.DataObjectIDColDuplicateKeyError(
                f"ID column '{self.root.id_col}' in root dataobject '{self.root.name}' has "
                "duplicates, which is not allowed"
            )