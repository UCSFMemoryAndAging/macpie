from typing import Tuple
import warnings

import numpy as np
import pandas as pd
import openpyxl as pyxl

from macpie._config import get_option
from macpie.core.dataset import Dataset
from macpie.core.datasetfields import DatasetFields
from macpie.util.info import Info
from macpie.exceptions import MergeableAnchoredListError, ParserError

from .anchoredlist import AnchoredList
from .basiclist import BasicList


class MergeableAnchoredList(AnchoredList):
    """

    """

    def __init__(
        self,
        primary: Dataset = None,
        secondary: BasicList = None,
        primary_anchor_field: Tuple[str, str] = None,
        secondary_anchor_col: str = None,
        selected_fields: DatasetFields = None
    ):
        self._primary_anchor_field = primary_anchor_field
        self._secondary_anchor_col = secondary_anchor_col
        self._selected_fields = selected_fields

        super().__init__(primary, secondary)

        self._validate()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'primary={self._primary!r}, '
            f'secondary={self._secondary!r}, '
            f'primary_anchor_field={self._primary_anchor_field!r}, '
            f'secondary_anchor_col={self._secondary_anchor_col!r}, '
            f'selected_fields={self._selected_fields!r})'
        )

    def _validate(self):
        if self._primary_anchor_field is None:  # default primary anchor column
            self._primary_anchor_field = (self._primary.name, self._primary.id_col)
        else:
            self._primary_anchor_field = tuple(self._primary_anchor_field)

        if self._secondary_anchor_col is None:  # default secondary anchor column
            self._secondary_anchor_col = self._primary.id_col + get_option("operators.binary.column_suffixes")[0]

        if self._selected_fields:
            self._selected_fields.prepend(self.key_fields, tags=[DatasetFields.tag_key_field])
            self._selected_fields.prepend(self.sys_fields, tags=[DatasetFields.tag_sys_field])
            self._selected_fields.sort(self)
            self.keep_fields(self._selected_fields)

    @property
    def key_fields(self):
        key_fields = super().key_fields
        if self._primary_anchor_field and self._primary_anchor_field not in key_fields:
            key_fields.append(self._primary_anchor_field)
        if self._secondary_anchor_col:
            for sec in self._secondary:
                sec_anchor_field = (sec.name, self._secondary_anchor_col)
                if sec_anchor_field not in key_fields:
                    key_fields.append(sec_anchor_field)
        return key_fields

    @property
    def merged_df(self):
        merged_df = self._primary.df.copy(deep=True)
        merged_df.columns = pd.MultiIndex.from_product([[self._primary.name], merged_df.columns])

        mergeable_secondary = self._secondary.filter(get_option("dataset.tag.linked"))

        for sec in mergeable_secondary:
            merged_df = merged_df.mac.merge(
                sec.df.copy(deep=True),
                left_on=[self._primary_anchor_field],
                right_on=[self._secondary_anchor_col],
                add_indexes=(None, sec.name)
            )

        # reset index to start from 1 for user readability
        start_index = 1
        merged_df.index = np.arange(start_index, len(merged_df) + start_index)
        return merged_df

    def add_secondary(self, dset: Dataset):
        if self._secondary_anchor_col not in dset.df.columns:
            warnings.warn(
                f"Warning: Secondary dataset '{dset!r}' does not have "
                f"anchor column '{self._secondary_anchor_col}'. Skipping..."
            )
            return

        secondary_tag = get_option("dataset.tag.secondary")
        mergeable_tag = get_option("dataset.tag.mergeable")
        duplicates_tag = get_option("dataset.tag.duplicates")
        linked_tag = get_option("dataset.tag.linked")

        dups = dset.df.duplicated(subset=self._secondary_anchor_col, keep=False)
        if dups.any():
            dups_col = get_option("column.system.duplicates")
            if dups_col in dset.sys_cols:
                dset.rename_col(dups_col, dups_col + '_prior')
            dset.df.mac.insert(dups_col, dups)
            dset.add_tag(duplicates_tag)
        else:
            dset.add_tag(mergeable_tag)

        super().add_secondary(dset)

        dset.replace_tag([secondary_tag, duplicates_tag], duplicates_tag)
        dset.replace_tag([secondary_tag, mergeable_tag], linked_tag)

    def get_available_fields(self):
        available_fields = DatasetFields.from_collection(
            self,
            tags=[get_option("dataset.tag.anchor"),
                  get_option("dataset.tag.linked"),
                  get_option("dataset.tag.duplicates")]
        )
        available_fields = available_fields.filter(DatasetFields.tag_non_key_field)
        available_fields.title = get_option("sheet.name.available_fields")
        available_fields.append_col_fill(None, header=get_option("column.to_merge"))
        return available_fields

    def to_dict(self):
        """
        Convert the MergeableAnchoredList to a dictionary.
        """
        return {
            'primary': self._primary,
            'secondary_linked': self._secondary.filter(get_option("dataset.tag.linked")),
            'secondary_duplicates': self._secondary.filter(get_option("dataset.tag.duplicates")),
            'primary_anchor_field': self._primary_anchor_field,
            'secondary_anchor_col': self._secondary_anchor_col,
            'selected_fields': self._selected_fields
        }

    def to_excel(self, excel_writer, merge: bool = True, **kwargs):
        if merge:
            self.merged_df.to_excel(excel_writer, sheet_name=get_option("sheet.name.merged_results", **kwargs))
        else:
            self._primary.to_excel(excel_writer, **kwargs)
            self._secondary.filter("linked").to_excel(excel_writer, **kwargs)

        self._secondary.filter(get_option("dataset.tag.duplicates")).to_excel(excel_writer, **kwargs)

        self.get_available_fields().to_excel(excel_writer, **kwargs)
        self.get_collection_info().to_excel(excel_writer, **kwargs)

    @classmethod
    def from_excel(cls, filepath) -> "MergeableAnchoredList":
        """
        Construct MergeableAnchoredList from an Excel file.
        """
        sheet_name = get_option("sheet.name.collection_info")
        try:
            info = Info.from_excel_sheet(filepath, sheet_name=sheet_name)
            info = info.to_dict()
        except Exception:
            raise MergeableAnchoredListError(
                f"Error reading sheet '{sheet_name}' from file."
            )

        if info['class_name'] != cls.__name__:
            raise TypeError(f"Excel file has info sheet of incorrect type: "
                            f"'{info['class_name']}' instead of '{cls.__name__}'")

        available_fields = DatasetFields.from_excel_sheet_create_tags(
            filepath,
            sheet_name=get_option("sheet.name.available_fields")
        )

        selected_fields = available_fields.filter(get_option("column.to_merge"))
        selected_fields.title = get_option("sheet.name.selected_fields")

        _primary = None
        _secondary = BasicList()
        _primary_anchor_field = None
        _secondary_anchor_col = None
        _selected_fields = selected_fields if len(selected_fields) > 0 else None

        wb = pyxl.load_workbook(filepath)

        primary_repr = info['primary']
        primary_sheet_name = Dataset.create_display_name(primary_repr['name'], primary_repr['tags'], max_length=31)
        if primary_sheet_name in wb.sheetnames:
            primary_df = pd.read_excel(filepath, sheet_name=primary_sheet_name, index_col=None, header=0)
            _primary = Dataset(primary_df,
                               id_col=primary_repr['id_col'],
                               date_col=primary_repr['date_col'],
                               id2_col=primary_repr['id2_col'],
                               name=primary_repr['name'])

            for sec in info['secondary_linked']:
                dset = Dataset.from_excel_sheet(filepath, sec, id_dropna=True)
                dset.clear_tags()
                _secondary.append(dset)
        else:
            merged_df_sheet_name = get_option("sheet.name.merged_results")
            if merged_df_sheet_name not in wb.sheetnames:
                raise ParserError(f"Excel sheet '{primary_sheet_name}' nor "
                                  f"'{merged_df_sheet_name}' not found in file: {filepath}")

            ws = wb[sheet_name]
            if ws['A2'].value == get_option("excel.row_index_header"):
                _merged_df = pd.read_excel(filepath, sheet_name=merged_df_sheet_name, index_col=0, header=[0, 1])
            else:
                _merged_df = pd.read_excel(filepath, sheet_name=merged_df_sheet_name, index_col=None, header=[0, 1])

            primary_name = info['primary']['name']
            primary_df = _merged_df.xs(primary_name, axis='columns', level=0)
            _primary = Dataset(primary_df,
                               id_col=info['primary']['id_col'],
                               date_col=info['primary']['date_col'],
                               id2_col=info['primary']['id2_col'],
                               name=primary_name)

            for sec in info['secondary_linked']:
                secondary_name = sec['name']
                secondary_df = _merged_df.xs(secondary_name, axis='columns', level=0)
                secondary_dset = Dataset(secondary_df,
                                         id_col=sec['id_col'],
                                         date_col=sec['date_col'],
                                         id2_col=sec['id2_col'],
                                         name=secondary_name)
                _secondary.append(secondary_dset)

        for sec in info['secondary_duplicates']:
            duplicate_dset = Dataset.from_excel_sheet(filepath, sec, id_dropna=True)
            duplicate_dset.clear_tags()
            _secondary.append(duplicate_dset)

        _primary_anchor_field = info['primary_anchor_field']
        _secondary_anchor_col = info['secondary_anchor_col']

        instance = cls(
            primary=_primary,
            secondary=_secondary,
            primary_anchor_field=_primary_anchor_field,
            secondary_anchor_col=_secondary_anchor_col,
            selected_fields=_selected_fields
        )

        return instance
