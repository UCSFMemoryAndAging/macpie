import itertools
import warnings
from collections import defaultdict

import numpy as np

from macpie._config import get_option
from macpie.core.collections.anchoredlist import AnchoredList
from macpie.core.collections.basiclist import BasicList
from macpie.core.dataset import Dataset
from macpie.core.datasetfields import DatasetFields
from macpie.io.excel._base import MACPieExcelFile
from macpie.tools import strtools


class MergeableAnchoredList(AnchoredList):
    """A :class:`macpie.AnchoredList` that is `mergeable`,
    meaning all ``secondary`` Datasets have a common column that can be
    used to merge with a column in the ``primary`` Dataset.
    Includes advanced duplicate handling functionality.

    :param primary: The primary `anchor` Dataset of the collection.
    :param secondary: The secondary Datasets of the collection.
    :param primary_anchor_col: The column in ``primary`` to merge on
    :param secondary_anchor_col: The column in each ``secondary`` Dataset
                                 to merge on
    :param selected_fields: Fields to keep (discarding the rest)
    """

    #: Tag that denotes a Dataset can be merged (i.e. no duplicates)
    tag_mergeable = "mergeable"

    #: Tag that denotes a Dataset has been merged (also means mergeable)
    tag_merged = "merged"

    #: Tag that denotes a Dataset has not been merged (though mergeable)
    tag_not_merged = "not_merged"

    #: Name of the merged dataset
    merged_dsetname = "MERGED_RESULTS"

    available_fields_sheetname = "_available_fields"
    selected_fields_sheetname = "_selected_fields"
    to_merge_column_name = "Merge?"

    def __init__(
        self,
        primary: Dataset = None,
        secondary: BasicList = None,
        primary_anchor_col=None,
        secondary_anchor_col=None,
        selected_fields: DatasetFields = None,
    ):
        self._merged_dset = None

        self._primary_anchor_col = primary_anchor_col
        self._secondary_anchor_col = secondary_anchor_col
        self._selected_fields = selected_fields

        super().__init__(primary, secondary)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"primary={self._primary!r}, "
            f"secondary={self._secondary!r}, "
            f"primary_anchor_col={self._primary_anchor_col!r}, "
            f"secondary_anchor_col={self._secondary_anchor_col!r}, "
            f"selected_fields={self._selected_fields!r})"
        )

    @AnchoredList.primary.setter
    def primary(self, dset: Dataset):
        """Sets the `primary` Dataset of this collection."""
        AnchoredList.primary.fset(self, dset)
        if self._primary is not None:
            if self._primary_anchor_col is None:
                self._primary_anchor_col = self._primary.id_col_name
            if self._secondary_anchor_col is None:
                self._secondary_anchor_col = (
                    self._primary.id_col_name + get_option("operators.binary.column_suffixes")[0]
                )

        # TODO: Check if there are any duplicates in the primary anchor column, and if so,
        # handle so that a merge can be properly done. Should be similar to the logic in the
        # add_secondary method.

    @property
    def merged_dset(self):
        """The merged data.

        :return: class:`pandas.DataFrame`
        """
        return self._merged_dset

    @property
    def key_fields(self):
        """A list of all :attr:`macpie.Dataset.key_fields` contained
        in this :class:`MergeableAnchoredList`.
        """
        key_fields = super().key_fields
        prim_anchor_field = (self._primary.name, self._primary_anchor_col)
        if self._primary_anchor_col and prim_anchor_field not in key_fields:
            key_fields.append(prim_anchor_field)
        if self._secondary_anchor_col:
            for sec in self._secondary:
                sec_anchor_field = (sec.name, self._secondary_anchor_col)
                if sec_anchor_field not in key_fields:
                    key_fields.append(sec_anchor_field)
        return key_fields

    @property
    def all_fields(self):
        """A list of all :attr:`macpie.Dataset.all_fields` contained
        in this :class:`MergeableAnchoredList`.
        """
        if not self._secondary_anchor_col:
            return super().all_fields

        fields = []
        if self._primary is not None:
            fields.extend(self._primary.all_fields)
        if self._secondary is not None:
            for sec in self._secondary:
                sec_anchor_field = (sec.name, self._secondary_anchor_col)
                fields.append(sec_anchor_field)
                fields.extend(sec.all_fields)
        return fields

    def add_secondary(self, dset: Dataset):
        """Append `dset` to :attr:`MergeableAnchoredList.secondary`."""
        if self._secondary_anchor_col not in dset.columns:
            warnings.warn(
                f"Warning: Secondary dataset '{dset!r}' does not have "
                f"anchor column '{self._secondary_anchor_col}'. Skipping..."
            )
            return

        dups = dset.duplicated(subset=[self._secondary_anchor_col], keep=False)
        if dups.any():
            dups_col = get_option("column.system.duplicates")
            if dups_col in dset.sys_cols:
                dset.rename_col(dups_col, dups_col + "_prior", inplace=True)
            dset.mac.insert(dups_col, dups)
            dset.add_tag(Dataset.tag_duplicates)
        else:
            dset.add_tag(MergeableAnchoredList.tag_mergeable)

        super().add_secondary(dset)

        dset.display_name_generator = MergeableAnchoredList.dataset_display_name_generator

        self._merged_dset = None

    def keep_fields(self, selected_fields, keep_unselected: bool = False, inplace=True):
        """Keep specified fields (and drop the rest).

        :param selected_fields: Fields to keep
        :param keep_unselected: If True, if a Dataset is not in ``selected_fields``,
                                then keep entire Dataset. Defaults to False.
        """
        fields_to_include = []
        selected_dsets = selected_fields.unique_datasets

        if self._primary.name not in selected_dsets:
            fields_to_include.extend(
                field for field in self.key_fields if field[0] == self._primary.name
            )

        fields_to_include.extend(
            [field for field in self.key_fields if field[0] in selected_dsets]
        )
        fields_to_include.extend(
            [field for field in self.sys_fields if field[0] in selected_dsets]
        )

        selected_fields.extendleft(fields_to_include)
        selected_fields.sort(self)

        if inplace:
            super().keep_fields(selected_fields, keep_unselected=keep_unselected, inplace=True)
        else:
            al = super().keep_fields(
                selected_fields, keep_unselected=keep_unselected, inplace=False
            )
            return MergeableAnchoredList(
                al.primary,
                al.secondary,
                self.primary_anchor_col,
                self.secondary_anchor_col,
                selected_fields,
            )

    def merge(self):
        """Perform the merge."""
        if self._selected_fields:
            self.keep_fields(self._selected_fields, keep_unselected=True, inplace=True)

        merged_dset = self._primary.prepend_level(self._primary.name)
        merged_dset.clear_tags()

        mergeable_secondary = self._secondary.filter(MergeableAnchoredList.tag_mergeable)

        for sec in mergeable_secondary:
            if self._selected_fields and sec.name not in self._selected_fields.unique_datasets:
                sec.add_tag(MergeableAnchoredList.tag_not_merged)
            else:
                if not sec.columns.is_unique:
                    # merge cannot handle a non-unique multi-index, so make
                    # them unique by appending numbers
                    # TODO: this belongs elsewhere? or perhaps drop them?
                    sec.columns = strtools.make_unique(
                        sec.columns.tolist(),
                        suffs_iter=itertools.count(2),
                        skip=1,
                        suffs_prefix="_",
                    )

                merged_dset = merged_dset.mac.merge(
                    sec.copy(deep=True),
                    left_on=[(self._primary.name, self._primary_anchor_col)],
                    right_on=[self._secondary_anchor_col],
                    add_indexes=(None, sec.name),
                )
                sec.add_tag(MergeableAnchoredList.tag_merged)

        # reset index to start from 1 for user readability
        start_index = 1
        merged_dset.index = np.arange(start_index, len(merged_dset) + start_index)

        self._merged_dset = merged_dset
        self._merged_dset.name = self.merged_dsetname

    def get_available_fields(self):
        """Get all "available" fields in this collection.

        :return: :class:`macpie.DatasetFields`
        """
        available_fields = DatasetFields.from_collection(
            self,
            tags=[
                MergeableAnchoredList.tag_anchor,
                MergeableAnchoredList.tag_mergeable,
                Dataset.tag_duplicates,
            ],
        )
        available_fields = available_fields.filter(DatasetFields.tag_non_key_field)
        available_fields.title = self.available_fields_sheetname
        return available_fields

    def get_duplicates(self):
        dup_dsets = self._secondary.filter(Dataset.tag_duplicates)

        if not dup_dsets:
            return {}

        result = defaultdict(list)

        for dset in dup_dsets:
            dup_rows_df = dset.duplicated(subset=[self._secondary_anchor_col], keep=False)
            result[dset.name].extend(dset[dup_rows_df].to_numpy())

        return result

    def to_excel_dict(self):
        """Convert the MergeableAnchoredList to a dictionary."""
        return {
            "class_name": self.__class__.__name__,
            "merged": self._merged_dset.to_excel_dict() if self._merged_dset is not None else None,
            "primary": self._primary.to_excel_dict(),
            "secondary": self._secondary.to_excel_dict(),
            "primary_anchor_col": self._primary_anchor_col,
            "secondary_anchor_col": self._secondary_anchor_col,
            "available_fields": self.get_available_fields().to_dict(),
            "selected_fields": self._selected_fields.to_dict() if self._selected_fields else None,
        }

    def to_excel(self, excel_writer, write_excel_dict=True, merge: bool = True, **kwargs):
        """Write :class:`MergeableAnchoredList` to an Excel file.

        :param merge: If True, output merged result. If False, keep everything
                      unmerged. Defaults to True.
        """
        if merge:
            if not self._merged_dset:
                self.merge()

            self._merged_dset.to_excel(excel_writer, **kwargs)

            self._secondary.filter([MergeableAnchoredList.tag_not_merged]).to_excel(
                excel_writer, write_excel_dict=False, **kwargs
            )
        else:
            self._primary.to_excel(excel_writer, **kwargs)
            self._secondary.filter([MergeableAnchoredList.tag_mergeable]).to_excel(
                excel_writer, write_excel_dict=False, **kwargs
            )

        self._secondary.filter(Dataset.tag_duplicates).to_excel(
            excel_writer, write_excel_dict=False, **kwargs
        )

        available_fields = self.get_available_fields()
        available_fields.append_col_fill(None, header=self.to_merge_column_name)

        excel_writer.write_tablib_dataset(available_fields)

        if write_excel_dict:
            excel_writer.write_excel_dict(self.to_excel_dict())

    @staticmethod
    def dataset_display_name_generator(dset: Dataset):
        suffixes = []
        if dset.tags:
            if MergeableAnchoredList.tag_mergeable in dset.tags:
                suffixes = ["linked"]
            elif Dataset.tag_duplicates in dset.tags:
                suffixes = ["DUPS"]
        return strtools.add_suffixes_with_base(dset.name, suffixes, max_length=-1, delimiter="_")

    @classmethod
    def from_excel_dict(cls, excel_file: MACPieExcelFile, excel_dict) -> "MergeableAnchoredList":
        """Construct :class:`MergeableAnchoredList` from an Excel file."""

        secondary_excel_dict = excel_dict["secondary"]

        available_fields = excel_file.parse_dataset_fields(
            sheet_name=MergeableAnchoredList.available_fields_sheetname
        )

        selected_fields = available_fields.filter(MergeableAnchoredList.to_merge_column_name)
        selected_fields.title = MergeableAnchoredList.selected_fields_sheetname

        _primary = None
        _secondary = BasicList()
        _primary_anchor_col = None
        _secondary_anchor_col = None
        _selected_fields = selected_fields if len(selected_fields) > 0 else None

        if excel_dict["merged"] is None:
            _primary = excel_file.parse(sheet_name=excel_dict["primary"]["excel_sheetname"])
        else:
            merged_dset = excel_file.parse(
                sheet_name=excel_dict["merged"]["excel_sheetname"],
                index_col=0,
                header=[0, 1],
            )

            _primary = merged_dset.cross_section(excel_dict["primary"])

            filtered_secondary_dict = BasicList.excel_dict_filter_tags(
                secondary_excel_dict, MergeableAnchoredList.tag_merged
            )

            for dset_dict in filtered_secondary_dict:
                secondary_dset = merged_dset.cross_section(dset_dict)
                secondary_dset.clear_tags()
                secondary_dset.drop_sys_cols()
                _secondary.append(secondary_dset)

        filtered_secondary_dict = BasicList.excel_dict_filterfalse_tags(
            secondary_excel_dict, MergeableAnchoredList.tag_merged
        )

        for dset_dict in filtered_secondary_dict:
            secondary_dset = excel_file.parse(sheet_name=dset_dict["excel_sheetname"])
            secondary_dset.clear_tags()
            secondary_dset.drop_sys_cols()
            _secondary.append(secondary_dset)

        _primary_anchor_col = excel_dict["primary_anchor_col"]
        _secondary_anchor_col = excel_dict["secondary_anchor_col"]

        instance = cls(
            primary=_primary,
            secondary=_secondary,
            primary_anchor_col=_primary_anchor_col,
            secondary_anchor_col=_secondary_anchor_col,
            selected_fields=_selected_fields,
        )
        return instance
