from abc import ABC, abstractmethod

from macpie._config import get_option
from macpie.util.info import Info


class BaseCollection(ABC):
    """

    """

    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @abstractmethod
    def to_dict(self):
        return {}

    def get_collection_info(self):
        collection_dict = {'class_name': self.__class__.__name__, **self.to_dict()}
        return Info.from_dict(collection_dict, title=get_option("sheet.name.collection_info"))

    def get_dataset_history_info(self):
        info = Info(title=get_option("sheet.name.dsets_history"))
        for dset in self:
            if dset.history:
                for record in dset.history:
                    info.append((dset.name, record))
        return info
