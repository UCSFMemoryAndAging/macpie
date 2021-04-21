from itertools import chain

from macpie._config import get_option
from macpie.core.dataset import Dataset
from macpie.util.datasetfields import DatasetFields

from .base import BaseCollection
from .basiclist import BasicList


class AnchoredList(BaseCollection):
    """

    """

    _tag_anchor = get_option("dataset.tag.anchor")
    _tag_secondary = get_option("dataset.tag.secondary")

    def __init__(self, primary: Dataset = None, secondary: BasicList = None):
        self._sheetname_available_fields = get_option("sheet.name.available_fields")

        if primary is None:
            self._primary = None
        else:
            self.set_primary(primary)

        if secondary is None:
            self._secondary = BasicList()
        else:
            self.set_secondary(secondary)

    def __setattr__(self, key, value):
        if key == '_primary' and key in self.__dict__ and self.__dict__[key] is not None:
            raise AttributeError(f"The value for the '{key}'' attribute has already "
                                 "been set, and can not be re-set")
        self.__dict__[key] = value

    def __iter__(self):
        return chain([self._primary] if self._primary else [], self._secondary)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'primary={self._primary!r}, '
            f'secondary={self._secondary!r}...)'
        )

    @property
    def primary(self):
        """The primary "anchor" Dataset of the collection.
           Cannot be directly modified.
        """
        return self._primary

    @property
    def secondary(self):
        """The secondary Datasets of the collection.
           Cannot be directly modified.
        """
        return self._secondary

    @property
    def all_fields(self):
        fields = []
        if self._primary:
            fields.extend(self._primary.all_fields)
        if self._secondary:
            for sec in self._secondary:
                fields.extend(sec.all_fields)
        return fields

    @property
    def key_fields(self):
        key_fields = []
        if self._primary:
            key_fields.extend(self._primary.key_fields)
        if self._secondary:
            for sec in self._secondary:
                key_fields.extend(sec.key_fields)
        return key_fields

    @property
    def sys_fields(self):
        sys_fields = []
        if self._primary:
            sys_fields.extend(self._primary.sys_fields)
        if self._secondary:
            for sec in self._secondary:
                sys_fields.extend(sec.sys_fields)
        return sys_fields

    def set_primary(self, dset: Dataset):
        if dset is None:
            raise ValueError("Cannot set Primary to None")
        if dset.df[dset.id_col].duplicated().any():
            raise ValueError("Primary Dataset in an AnchoredList cannot have duplicate IDs")
        self._primary = dset
        self._primary.sort_by_id2()
        self._primary.add_tag(AnchoredList._tag_anchor)

    def set_secondary(self, dsets: BasicList):
        if dsets is None:
            raise ValueError("Cannot set Secondary to None")
        self._secondary = BasicList()
        for sec in dsets:
            self.add_secondary(sec)

    def add_secondary(self, dset: Dataset, tags=list()):
        dset.add_tag(AnchoredList._tag_secondary)
        self._secondary.append(dset)

    def keep_fields(self, selected_fields, keep_unselected: bool = False):
        if self._primary:
            self._primary.keep_fields(selected_fields)
        if self._secondary:
            self._secondary.keep_fields(selected_fields, keep_unselected=keep_unselected)

    def get_available_fields(self):
        return DatasetFields.from_collection(self, title=self._sheetname_available_fields)

    def to_excel(self, excel_writer, **kwargs):
        self._primary.to_excel(excel_writer, **kwargs)
        self._secondary.to_excel(excel_writer, **kwargs)

        self.get_collection_info().to_excel(excel_writer, **kwargs)
