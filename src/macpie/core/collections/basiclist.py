from collections import UserList

from macpie.core.dataset import Dataset
from macpie.core.datasetfields import DatasetFields
from macpie.core.collections.base import BaseCollection
from macpie.io.excel._base import MACPieExcelFile


class BasicList(UserList, BaseCollection):
    """A basic list of Datasets."""

    @property
    def dsets(self):
        """The list of Datasets."""
        return self.data

    def filter(self, tag):
        """Returns a new instance of :class:`BasicList`, excluding any
        :class:`macpie.Dataset` objects that do not contain the given ``tag``.
        """
        return BasicList([dset for dset in self.data if dset.has_tag(tag)])

    def replace_tag(self, old_tag, new_tag):
        """Iterate over Datasets in this list and
        replace ``old_tag`` with ``new_tag``.
        """
        for dset in self.dsets:
            dset.replace_tag(old_tag, new_tag)

    def keep_fields(
        self, selected_fields: DatasetFields, keep_unselected: bool = False, inplace=False
    ):
        """Keep specified fields (and drop the rest).

        :param selected_fields: Fields to keep
        :param keep_unselected: If True, if a Dataset is not in ``selected_fields``,
                                then keep entire Dataset. Defaults to False.
        """
        new_list = []
        for dset in self.data:
            if dset.name in selected_fields.unique_datasets:
                dset = dset.keep_fields(selected_fields)
                new_list.append(dset)
            elif keep_unselected:
                new_list.append(dset.copy())

        if inplace:
            self.data = new_list
        else:
            return BasicList(new_list)

    def to_excel(self, excel_writer, write_excel_dict=True, **kwargs):
        """Write :class:`BasicList` to an Excel file by calling
        :meth:`macpie.Dataset.to_excel` on each :class:`macpie.Dataset`
        in this list.
        """
        for dset in self.data:
            dset.to_excel(excel_writer, **kwargs)

        if write_excel_dict:
            excel_writer.write_excel_dict(self.to_excel_dict())

    def to_excel_dict(self):
        """Convert the :class:`BasicList` to a dictionary."""
        excel_dict = {"class_name": self.__class__.__name__}
        excel_dict.update({"dsets": [dset.to_excel_dict() for dset in self.data]})
        return excel_dict

    @staticmethod
    def excel_dict_dsets(excel_dict):
        if excel_dict["class_name"] == "BasicList" and "dsets" in excel_dict:
            return excel_dict["dsets"]
        return {}

    @staticmethod
    def excel_dict_filter_tags(excel_dict, tags):
        excel_dict_dsets = BasicList.excel_dict_dsets(excel_dict)
        return [
            excel_dict_dset
            for excel_dict_dset in excel_dict_dsets
            if Dataset.excel_dict_has_tags(excel_dict_dset, tags)
        ]

    @staticmethod
    def excel_dict_filterfalse_tags(excel_dict, tags):
        excel_dict_dsets = BasicList.excel_dict_dsets(excel_dict)
        return [
            excel_dict_dset
            for excel_dict_dset in excel_dict_dsets
            if not Dataset.excel_dict_has_tags(excel_dict_dset, tags)
        ]

    @classmethod
    def from_excel_dict(cls, excel_file: MACPieExcelFile, excel_dict):
        instance = cls()
        excel_dict_dsets = BasicList.excel_dict_dsets(excel_dict)
        for dset_excel_dict in excel_dict_dsets:
            dset = excel_file.parse(sheet_name=dset_excel_dict["excel_sheetname"])
            instance.append(dset)
        return instance
