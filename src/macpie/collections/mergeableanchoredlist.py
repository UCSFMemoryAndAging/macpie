import warnings

import numpy as np
import pandas as pd
import openpyxl as pyxl

from macpie._config import get_option
from macpie.core.dataset import Dataset
from macpie.util.datasetfields import DatasetFields
from macpie.util.info import Info
from macpie.exceptions import MergeableAnchoredListError, ParserError
from macpie.tools import string as strtools

from .anchoredlist import AnchoredList
from .basiclist import BasicList


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
    tag_mergeable = get_option("dataset.tag.mergeable")

    #: Tag that denotes a Dataset has been merged (also means mergeable)
    tag_merged = get_option("dataset.tag.merged")

    #: Tag that denotes a Dataset has not been merged (though mergeable)
    tag_not_merged = get_option("dataset.tag.not_merged")

    #: Tag that denotes a Dataset cannot be merged (i.e. has duplicates)
    tag_duplicates = get_option("dataset.tag.duplicates")

    def __init__(
        self,
        primary: Dataset = None,
        secondary: BasicList = None,
        primary_anchor_col: str = None,
        secondary_anchor_col: str = None,
        selected_fields: DatasetFields = None
    ):
        self._merged_df = None

        self._primary_anchor_col = primary_anchor_col
        self._secondary_anchor_col = secondary_anchor_col
        self._selected_fields = selected_fields

        super().__init__(primary, secondary)

        self._validate()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'primary={self._primary!r}, '
            f'secondary={self._secondary!r}, '
            f'primary_anchor_col={self._primary_anchor_col!r}, '
            f'secondary_anchor_col={self._secondary_anchor_col!r}, '
            f'selected_fields={self._selected_fields!r})'
        )

    def _validate(self):
        if self._primary_anchor_col is None:  # default primary anchor column
            self._primary_anchor_col = self._primary.id_col
        else:
            self._primary_anchor_col = self._primary_anchor_col

        if self._secondary_anchor_col is None:  # default secondary anchor column
            self._secondary_anchor_col = self._primary.id_col + get_option("operators.binary.column_suffixes")[0]

    @property
    def merged_df(self):
        """The merged data.

        :return: class:`pandas.DataFrame`
        """
        return self._merged_df

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
        if self._primary:
            fields.extend(self._primary.all_fields)
        if self._secondary:
            for sec in self._secondary:
                sec_anchor_field = (sec.name, self._secondary_anchor_col)
                fields.append(sec_anchor_field)
                fields.extend(sec.all_fields)
        return fields

    def add_secondary(self, dset: Dataset):
        """Append `dset` to :attr:`MergeableAnchoredList.secondary`.
        """
        if self._secondary_anchor_col not in dset.df.columns:
            warnings.warn(
                f"Warning: Secondary dataset '{dset!r}' does not have "
                f"anchor column '{self._secondary_anchor_col}'. Skipping..."
            )
            return

        dups = dset.df.duplicated(subset=[self._secondary_anchor_col], keep=False)
        if dups.any():
            dups_col = get_option("column.system.duplicates")
            if dups_col in dset.sys_cols:
                dset.rename_col(dups_col, dups_col + '_prior')
            dset.df.mac.insert(dups_col, dups)
            dset.add_tag(MergeableAnchoredList.tag_duplicates)
        else:
            dset.add_tag(MergeableAnchoredList.tag_mergeable)

        super().add_secondary(dset)

        dset.display_name_generator = MergeableAnchoredList.get_dataset_display_name_generator()

        self._merged_df = None

    def keep_fields(self, selected_fields, keep_unselected: bool = False):
        """Keep specified fields (and drop the rest).

        :param selected_fields: Fields to keep
        :param keep_unselected: If True, if a Dataset is not in ``selected_fields``,
                                then keep entire Dataset. Defaults to False.
        """
        fields_to_include = []
        selected_dsets = selected_fields.datasets

        if self._primary.name not in selected_dsets:
            fields_to_include.extend(field for field in self.key_fields if field[0] == self._primary.name)

        fields_to_include.extend([field for field in self.key_fields if field[0] in selected_dsets])
        fields_to_include.extend([field for field in self.sys_fields if field[0] in selected_dsets])

        selected_fields.prepend(fields_to_include)
        selected_fields.sort(self)

        super().keep_fields(selected_fields, keep_unselected=keep_unselected)

    def merge(self):
        """Perform the merge.
        """
        if self._selected_fields:
            self.keep_fields(self._selected_fields, keep_unselected=True)

        merged_df = self._primary.df.copy(deep=True)
        merged_df.columns = pd.MultiIndex.from_product([[self._primary.name], merged_df.columns])

        mergeable_secondary = self._secondary.filter(MergeableAnchoredList.tag_mergeable)

        for sec in mergeable_secondary:
            if self._selected_fields and sec.name not in self._selected_fields.datasets:
                sec.add_tag(MergeableAnchoredList.tag_not_merged)
            else:
                merged_df = merged_df.mac.merge(
                    sec.df.copy(deep=True),
                    left_on=[(self._primary.name, self._primary_anchor_col)],
                    right_on=[self._secondary_anchor_col],
                    add_indexes=(None, sec.name)
                )
                sec.add_tag(MergeableAnchoredList.tag_merged)

        # reset index to start from 1 for user readability
        start_index = 1
        merged_df.index = np.arange(start_index, len(merged_df) + start_index)

        self._merged_df = merged_df

    def get_available_fields(self):
        """Get all "available" fields in this collection.

        :return: :class:`macpie.util.DatasetFields`
        """
        available_fields = DatasetFields.from_collection(
            self,
            tags=[MergeableAnchoredList.tag_anchor,
                  MergeableAnchoredList.tag_mergeable,
                  MergeableAnchoredList.tag_duplicates]
        )
        available_fields = available_fields.filter(DatasetFields.tag_non_key_field)
        available_fields.title = self._sheetname_available_fields
        available_fields.append_col_fill(None, header=get_option("column.to_merge"))
        return available_fields

    def get_duplicates(self):
        dup_dsets = self._secondary.filter(MergeableAnchoredList.tag_duplicates)

        if not dup_dsets:
            return {}

        result = {}

        for dset in dup_dsets:
            result[dset.name] = []

        for dset in dup_dsets:
            dup_rows_df = dset.df.duplicated(subset=[self._secondary_anchor_col], keep=False)
            result[dset.name].extend(dset.df[dup_rows_df].values.tolist())

        return result

    def to_dict(self):
        """Convert the MergeableAnchoredList to a dictionary.
        """
        return {
            'primary': self._primary,
            'secondary': self._secondary,
            'primary_anchor_col': self._primary_anchor_col,
            'secondary_anchor_col': self._secondary_anchor_col,
            'selected_fields': self._selected_fields
        }

    def to_excel(self, excel_writer, merge: bool = True, **kwargs):
        """Write :class:`MergeableAnchoredList` to an Excel file.

        :param merge: If True, output merged result. If False, keep everything
                      unmerged. Defaults to True.
        """

        if merge:
            if not self._merged_df:
                self.merge()
            self._merged_df.to_excel(excel_writer, sheet_name=get_option("sheet.name.merged_results", **kwargs))
            self._secondary.filter([MergeableAnchoredList.tag_not_merged]).to_excel(excel_writer, **kwargs)
        else:
            self._primary.to_excel(excel_writer, **kwargs)
            self._secondary.filter([MergeableAnchoredList.tag_mergeable]).to_excel(excel_writer, **kwargs)

        self._secondary.filter(MergeableAnchoredList.tag_duplicates).to_excel(excel_writer, **kwargs)

        self.get_available_fields().to_excel(excel_writer, **kwargs)
        self.get_collection_info().to_excel(excel_writer, **kwargs)

    @classmethod
    def get_dataset_display_name_generator(cls):
        def dataset_display_name_generator(name, tags, max_length: int = -1, delimiter: str = '_'):
            if not tags:
                return name[:max_length] if max_length > -1 else name

            suffix = ""
            if cls.tag_mergeable in tags:
                suffix = "linked"
            elif cls.tag_duplicates in tags:
                suffix = "DUPS"

            return strtools.add_suffixes_with_base(name, [suffix])

        return dataset_display_name_generator

    @classmethod
    def from_excel(cls, filepath) -> "MergeableAnchoredList":
        """Construct :class:`MergeableAnchoredList` from an Excel file.
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
        _primary_anchor_col = None
        _secondary_anchor_col = None
        _selected_fields = selected_fields if len(selected_fields) > 0 else None

        wb = pyxl.load_workbook(filepath)

        primary_repr = info['primary']
        primary_sheetname = primary_repr['excel_sheetname']

        if primary_sheetname in wb.sheetnames:  # collection was not merged
            primary_df = pd.read_excel(filepath, sheet_name=primary_sheetname, index_col=None, header=0)
            _primary = Dataset(primary_df,
                               id_col=primary_repr['id_col'],
                               date_col=primary_repr['date_col'],
                               id2_col=primary_repr['id2_col'],
                               name=primary_repr['name'])

        else:  # collection was merged
            merged_df_sheet_name = get_option("sheet.name.merged_results")
            if merged_df_sheet_name not in wb.sheetnames:
                raise ParserError(f"Excel sheet '{primary_sheetname}' nor "
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

            for sec in info['secondary']:
                secondary_name = sec['name']
                secondary_tags = sec['tags']

                if MergeableAnchoredList.tag_merged in secondary_tags:
                    secondary_df = _merged_df.xs(secondary_name, axis='columns', level=0)
                    secondary_dset = Dataset(secondary_df,
                                             id_col=sec['id_col'],
                                             date_col=sec['date_col'],
                                             id2_col=sec['id2_col'],
                                             name=secondary_name)
                    secondary_dset.clear_tags()
                    secondary_dset.drop_sys_cols()
                    _secondary.append(secondary_dset)

        for sec in info['secondary']:
            secondary_tags = sec['tags']
            if MergeableAnchoredList.tag_merged not in secondary_tags:
                secondary_dset = Dataset.from_excel_sheet(filepath, sec)
                secondary_dset.clear_tags()
                secondary_dset.drop_sys_cols()
                _secondary.append(secondary_dset)

        _primary_anchor_col = info['primary_anchor_col']
        _secondary_anchor_col = info['secondary_anchor_col']

        instance = cls(
            primary=_primary,
            secondary=_secondary,
            primary_anchor_col=_primary_anchor_col,
            secondary_anchor_col=_secondary_anchor_col,
            selected_fields=_selected_fields
        )

        return instance
