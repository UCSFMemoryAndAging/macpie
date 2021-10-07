from collections import UserList
from collections.abc import MutableSequence

from copy import copy
import re
from typing import List

from macpie import Dataset, DatasetFields
from macpie.io.excel import read_excel

from .base import BaseCollection


class BasicList(UserList, BaseCollection):
    """A basic list of Datasets."""

    @property
    def dsets(self):
        """The list of Datasets."""
        return self.data

    @property
    def key_fields(self):
        """A list of all :attr:`macpie.Dataset.key_fields` contained
        in this :class:`BasicList`.
        """
        key_fields = []
        for dset in self.data:
            key_fields.extend(dset.key_fields)

    def filter(self, tag):
        """Returns a new instance of :class:`BasicList`, excluding any
        :class:`macpie.Dataset` objects that do not contain the given ``tag``.
        """
        return BasicList([dset for dset in self.data if dset.has_tag(tag)])

    def replace_tag(self, old_tag, new_tag):
        """Iterate over Datasets in this list and
        replace ``old_tag`` with ``new_tag``.
        """
        for dset in self.data:
            dset.replace_tag(old_tag, new_tag)

    def keep_fields(self, selected_fields: DatasetFields, keep_unselected: bool = False):
        """Keep specified fields (and drop the rest).

        :param selected_fields: Fields to keep
        :param keep_unselected: If True, if a Dataset is not in ``selected_fields``,
                                then keep entire Dataset. Defaults to False.
        """
        new_list = []
        for dset in self.data:
            if dset.name in selected_fields.to_dict():
                dset.keep_fields(selected_fields)
                new_list.append(dset)
            elif keep_unselected:
                new_list.append(dset)
        self.dsets = new_list

    def to_excel(self, excel_writer, write_repr=True, **kwargs):
        """Write :class:`BasicList` to an Excel file by calling
        :meth:`macpie.Dataset.to_excel` on each :class:`macpie.Dataset`
        in this list.
        """
        for dset in self.data:
            dset.to_excel(excel_writer, **kwargs)
        if write_repr:
            self.get_excel_repr().to_excel(excel_writer, dump_json=True)

    def to_excel_dict(self):
        """Convert the :class:`BasicList` to a dictionary."""
        excel_dict = {"class_name": self.__class__.__name__}
        excel_dict.update({dset.get_excel_sheetname(): dset.to_excel_dict() for dset in self.data})
        return excel_dict

    @classmethod
    def from_excel_dict(cls, filepath, excel_dict):
        instance = cls()
        print("ecel_dic", excel_dict)
        for value in excel_dict.values():
            print("value", value)
            if type(value) is dict and value["class_name"] == "Dataset":
                dset = read_excel(filepath, sheet_name=value["excel_sheetname"])
                instance.append(dset)
        return instance
