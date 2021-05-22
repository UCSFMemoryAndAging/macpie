from copy import copy
from typing import List

from macpie.core.dataset import Dataset
from macpie.util.datasetfields import DatasetFields

from .base import BaseCollection


class BasicList(BaseCollection):
    """A basic list of Datasets.
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
        """The list of Datasets.
        """
        return self._dsets

    @dsets.setter
    def dsets(self, value):
        if value is None:
            self._dsets = []
        else:
            self._dsets = list(dset for dset in value)

    @property
    def key_fields(self):
        """A list of all :attr:`macpie.Dataset.key_fields` contained
        in this :class:`BasicList`.
        """
        key_fields = []
        for dset in self._dsets:
            key_fields.extend(dset.key_fields)

    def append(self, dset):
        """Append ``dset`` to this :class:`BasicList`.
        """
        self._dsets.append(dset)

    def extend(self, dsets):
        """Append all elements in ``dsets`` to this :class:`BasicList`.
        """
        for dset in dsets:
            self.append(dset)

    def filter(self, tag):
        """Returns a new instance of :class:`BasicList`, excluding any
        :class:`macpie.Dataset` objects that do not contain the given ``tag``.
        """
        _dsetlist = copy(self)
        _dsetlist._dsets = [dset for dset in self._dsets if dset.has_tag(tag)]
        return _dsetlist

    def replace_tag(self, old_tag, new_tag):
        """Iterate over Datasets in this list and
        replace ``old_tag`` with ``new_tag``.
        """

        for dset in self._dsets:
            dset.replace_tag(old_tag, new_tag)

    def keep_fields(self, selected_fields: DatasetFields, keep_unselected: bool = False):
        """Keep specified fields (and drop the rest).

        :param selected_fields: Fields to keep
        :param keep_unselected: If True, if a Dataset is not in ``selected_fields``,
                                then keep entire Dataset. Defaults to False.
        """
        new_list = []
        for dset in self._dsets:
            if dset.name in selected_fields.to_dict():
                dset.keep_fields(selected_fields)
                new_list.append(dset)
            elif keep_unselected:
                new_list.append(dset)
        self.dsets = new_list

    def to_excel(self, excel_writer, **kwargs):
        """Write :class:`BasicList` to an Excel file by calling
        :meth:`macpie.Dataset.to_excel` on each :class:`macpie.Dataset`
        in this list.
        """
        for dset in self._dsets:
            dset.to_excel(excel_writer, **kwargs)

    def to_dict(self):
        """Convert the :class:`BasicList` to a dictionary.
        """
        return {"dsets": self._dsets}

    def to_json_dict(self):
        """Convert the :class:`BasicList` to a dictionary suitable for JSON.
        """
        return self._dsets
