from copy import copy
from typing import List

from macpie.core.dataset import Dataset

from .base import BaseCollection


class BasicList(BaseCollection):
    """

    """

    def __init__(self, dsets: List[Dataset] = []):
        self.dsets = dsets

    def __iter__(self):
        return (dset for dset in self._dsets)

    def __len__(self):
        return len(self._dsets)

    def __repr__(self):
        return repr(self._dsets)

    def __getitem__(self, i):
        return self._dsets[i]

    def __setitem__(self, i, value):
        self._dsets[i] = value

    def __delitem__(self, i):
        del self._dsets[i]

    @property
    def dsets(self):
        return self._dsets

    @dsets.setter
    def dsets(self, value):
        if value is None:
            self._dsets = []
        else:
            self._dsets = list(dset for dset in value)

    @property
    def key_fields(self):
        key_fields = []
        for dset in self._dsets:
            key_fields.extend(dset.key_fields)

    def append(self, dset):
        self._dsets.append(dset)

    def extend(self, dsets):
        for dset in dsets:
            self.append(dset)

    def filter(self, tag):
        _dsetlist = copy(self)
        _dsetlist._dsets = [dset for dset in self._dsets if dset.has_tag(tag)]
        return _dsetlist

    def replace_tag(self, old_tag, new_tag):
        for dset in self._dsets:
            dset.replace_tag(old_tag, new_tag)

    def keep_fields(self, selected_fields):
        new_list = []
        for dset in self._dsets:
            if dset.name in selected_fields.to_dict():
                dset.keep_fields(selected_fields)
                new_list.append(dset)
        self.dsets = new_list

    def to_excel(self, excel_writer, **kwargs):
        for dset in self._dsets:
            dset.to_excel(excel_writer, **kwargs)

    def to_dict(self):
        return {"dsets": self._dsets}

    def to_json(self):
        return self._dsets
