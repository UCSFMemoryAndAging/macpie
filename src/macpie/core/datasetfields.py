import collections
from typing import NamedTuple

from macpie.tools import tablibtools


class DatasetField(NamedTuple):
    dataset: str
    field: str


class DatasetFields(tablibtools.MacpieTablibDataset):
    """A tabular representation of a set of :class:`macpie.Dataset` fields.
    First column is the Dataset name. Second column is the Dataset column name.

    It is a subclass of :class:`macpie.tablibtools.MacpieTablibDataset`, and therefore
    can be initialized with data the same way.
    """

    #: Tag to indicate key fields
    tag_key_field = "key_field"

    #: Tag to indicate non-key fields
    tag_non_key_field = "non_key_field"

    #: Tag to indicate system fields
    tag_sys_field = "sys_field"

    def __init__(self, *args, **kwargs):
        self._col_header_dataset = "Dataset"
        self._col_header_field = "Field"

        headers = kwargs.pop("headers", (self._col_header_dataset, self._col_header_field))
        super().__init__(*args, headers=headers, **kwargs)

    def __iter__(self):
        return (DatasetField(row[0], row[1]) for row in self.data)

    @property
    def unique_datasets(self):
        """A list of unique :class:`macpie.Dataset` names."""
        return list(set(self[self._col_header_dataset]))

    def sort(self, collection):
        """Sort the Dataset fields according to the order they have in
        their respective collections.
        """
        fields = [field for field in self]
        fields.sort(key=lambda i: collection.all_fields.index(i))
        self.wipe_data()
        self.extend(fields)

    def to_dict(self):
        """Convert this :class:`DatasetFields` to a dictionary."""
        d = collections.defaultdict(list)
        for dataset_field in self:
            d[dataset_field.dataset].append(dataset_field.field)
        return d

    @classmethod
    def from_collection(cls, collection, **kwargs) -> "DatasetFields":
        """Construct :class:`DatasetFields` from a MACPie Collection."""
        tags = kwargs.pop("tags", [])
        instance = cls(**kwargs)

        for dset in collection:
            if tags and not dset.has_tag(tags):
                continue
            for col in dset.columns:
                field = DatasetField(dset.name, col)
                if field in collection.key_fields:
                    instance.append(field, tags=[DatasetFields.tag_key_field] + tags)
                elif field in collection.sys_fields:
                    instance.append(field, tags=[DatasetFields.tag_sys_field] + tags)
                else:
                    instance.append(field, tags=[DatasetFields.tag_non_key_field] + tags)

        return instance
