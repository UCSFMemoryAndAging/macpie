from itertools import chain

from macpie._config import get_option
from macpie.core.dataset import Dataset
from macpie.util.datasetfields import DatasetFields

from .base import BaseCollection
from .basiclist import BasicList


class AnchoredList(BaseCollection):
    """
    A collection of Datasets where one is considered the `primary`
    or `anchor` Dataset, and the rest are considered `secondary` Datasets.

    :param primary: The primary `anchor` Dataset of the collection.
    :param secondary: The secondary Datasets of the collection.

    """

    #: Tag that gets added to the `primary` Dataset
    tag_anchor = get_option("dataset.tag.anchor")

    #: Tag that gets added to all the `secondary` Datasets
    tag_secondary = get_option("dataset.tag.secondary")

    def __init__(self, primary: Dataset = None, secondary: BasicList = None):
        self._sheetname_available_fields = get_option("sheet.name.available_fields")

        self.primary = primary
        self.secondary = secondary

    def __iter__(self):
        return chain([self._primary] if self._primary else [], self._secondary)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"primary={self._primary!r}, "
            f"secondary={self._secondary!r}...)"
        )

    @property
    def primary(self):
        """The primary `anchor` Dataset of the collection."""
        return self._primary

    @primary.setter
    def primary(self, dset: Dataset):
        """Sets the `primary` Dataset of this collection."""
        if hasattr(self, "_primary") and self._primary is not None:
            raise AttributeError(
                "The 'primary' attribute has already been set, and can not be re-set."
            )

        if dset and dset.df[dset.id_col].duplicated().any():
            raise ValueError("Primary Dataset in an AnchoredList cannot have duplicate IDs")

        self._primary = dset

        if self._primary:
            self._primary.sort_by_id2()
            self._primary.add_tag(AnchoredList.tag_anchor)

    @property
    def secondary(self):
        """The secondary Datasets of the collection.
        Cannot be directly modified.
        """
        return self._secondary

    @secondary.setter
    def secondary(self, dsets: BasicList):
        """Sets the `secondary` Datasets of this collection."""
        self._secondary = BasicList()
        if dsets is not None:
            for sec in dsets:
                self.add_secondary(sec)

    @property
    def key_fields(self):
        """A list of all :attr:`macpie.Dataset.key_fields` contained
        in this :class:`AnchoredList`.
        """
        key_fields = []
        if self._primary:
            key_fields.extend(self._primary.key_fields)
        if self._secondary:
            for sec in self._secondary:
                key_fields.extend(sec.key_fields)
        return key_fields

    @property
    def sys_fields(self):
        """A list of all :attr:`macpie.Dataset.sys_fields` contained
        in this :class:`AnchoredList`.
        """
        sys_fields = []
        if self._primary:
            sys_fields.extend(self._primary.sys_fields)
        if self._secondary:
            for sec in self._secondary:
                sys_fields.extend(sec.sys_fields)
        return sys_fields

    @property
    def all_fields(self):
        """A list of all :attr:`macpie.Dataset.all_fields` contained
        in this :class:`AnchoredList`.
        """
        fields = []
        if self._primary:
            fields.extend(self._primary.all_fields)
        if self._secondary:
            for sec in self._secondary:
                fields.extend(sec.all_fields)
        return fields

    def add_secondary(self, dset: Dataset):
        """Append `dset` to :attr:`AnchoredList.secondary`."""
        dset.add_tag(AnchoredList.tag_secondary)
        self._secondary.append(dset)

    def keep_fields(self, selected_fields, keep_unselected: bool = False):
        """Keep specified fields (and drop the rest).

        :param selected_fields: Fields to keep
        :param keep_unselected: If True, if a Dataset is not in ``selected_fields``,
                                then keep entire Dataset. Defaults to False.
        """
        if self._primary:
            self._primary.keep_fields(selected_fields)
        if self._secondary:
            self._secondary.keep_fields(selected_fields, keep_unselected=keep_unselected)

    def get_available_fields(self):
        """Get all "available" fields in this collection.

        :return: :class:`macpie.util.DatasetFields`
        """
        return DatasetFields.from_collection(self, title=self._sheetname_available_fields)

    def to_dict(self):
        """Convert the AnchoredList to a dictionary."""
        return {"primary": self._primary, "secondary": self._secondary}

    def to_excel(self, excel_writer, **kwargs):
        """Write :class:`AnchoredList` to an Excel file by calling
        :meth:`macpie.Dataset.to_excel` on :attr:`AnchoredList.primary`
        and :attr:`AnchoredList.secondary`.
        """
        self._primary.to_excel(excel_writer, **kwargs)
        self._secondary.to_excel(excel_writer, **kwargs)

        self.get_collection_info().to_excel(excel_writer, **kwargs)
