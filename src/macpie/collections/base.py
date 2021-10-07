from abc import abstractmethod
from collections.abc import Collection
import json

from macpie._config import get_option
from macpie.io.excel import MACPieExcelFile
from macpie.util.simpledataset import DictLikeDataset


class BaseCollection(Collection):
    """Abstract base class for all collections."""

    def __contains__(self, x):
        return False

    def __iter__(self):
        while False:
            yield None

    def __len__(self):
        return 0

    @abstractmethod
    def to_excel_dict(self):
        return {}

    def get_excel_repr(self):
        """Contruct and return an :class:`macpie.core.DictLikeDataset` object
        describing this collection.
        """
        dictionary = {"class_name": self.__class__.__name__}
        dictionary.update(self.to_excel_dict())
        return DictLikeDataset.from_dict(dictionary, title=MACPieExcelFile._collection_sheet_name)

    def get_dataset_history_info(self):
        """Contruct and return an :class:`macpie.core.DictLikeDataset` object containing
        all :attr:`macpie.Dataset.history` information.
        """
        info = DictLikeDataset(title=get_option("excel.sheet_name.dsets_history"))
        for dset in self:
            if dset.history:
                for record in dset.history:
                    info.append((dset.name, record))
        return info
