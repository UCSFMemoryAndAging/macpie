from collections import defaultdict, deque, namedtuple, UserList
from typing import List, NamedTuple, Optional
import pandas as pd

from macpie._config import get_option
from macpie.tools import tablib as tablibtools
from macpie.util.simpledataset import SimpleDataset


class DatasetField(NamedTuple):
    dataset: str
    field: str


class DatasetFields(SimpleDataset):
    """A tabular representation of a set of :class:`macpie.Dataset` fields.
    First column is the Dataset name.
    Second column is the Dataset column name.

    It is a subclass of :class:`macpie.tablibtools.SimpleDataset`, and therefore
    can be initialized with data the same way.
    """

    tag_key_field = "key_field"
    tag_non_key_field = "non_key_field"
    tag_sys_field = "sys_field"

    def __init__(self, *args, **kwargs):
        self._col_header_dataset = get_option("column.dataset")
        self._col_header_field = get_option("column.field")

        headers = kwargs.pop("headers", (self._col_header_dataset, self._col_header_field))
        super().__init__(*args, headers=headers, **kwargs)

    @property
    def unique_datasets(self):
        """A list of unique :class:`macpie.Dataset` names."""
        return set(self.datasets)

    def append_with_tags(self, ser: pd.Series, tag_value: str = "x"):
        """Adds ``ser`` as a row to ``dset`` with tags derived
        from the labels in ``ser`` that are not headers in ``dset``,
        and whose value is ``'x'`` or ``'X'``.

            >>> dset = tl.Dataset()
            >>> dset.headers = ('Dataset', 'Field')
            >>> dset.append(('CDR', 'Col1'))
            >>> dset.export("df")
            Dataset Field
            0     CDR  Col1
            >>> ser_data = {'Dataset':'CDR', 'Field':'Col2', 'Merge?': 'x'}
            >>> ser = pd.Series(data=ser_data, index=['Dataset','Field','Merge?'])
            >>> ser
            Dataset     CDR
            Field      Col2
            Merge?        x
            >>> mp.tablibtools.append_with_tags(dset, ser)
            >>> dset.export("df")
            Dataset Field
            0     CDR  Col1
            1     CDR  Col2
            >>> dset2 = dset.filter('Merge?')
            Dataset Field
            0     CDR  Col2

        :param dset: The :class:`tablib.Dataset` that gets ``ser`` appended to
        :param ser: A row of data to append to ``dset``
        """
        ser = ser.copy()
        tag_value = tag_value.lower()
        dataset = ser.pop(item=self._col_header_dataset)
        field = ser.pop(item=self._col_header_field)
        tags = ser[ser.str.lower() == tag_value].index.tolist()
        self.append(DatasetField(dataset, field), tags=tags)

    def extendleft(self, dataset_fields, tags=()):
        """Prepend a list of Dataset fields."""
        other_fields = [field for field in self]
        self.wipe_data()
        self.extend(dataset_fields, tags=tags)
        self.extend(other_fields)

    def sort(self, collection):
        """Sort the Dataset fields according to the order they have in
        their respective collections.
        """
        fields = [field for field in self]
        fields.sort(key=lambda i: collection.all_fields.index(i))
        self.wipe_data()
        self.extend(fields)

    """
    def to_excel(self, excel_writer, sheet_name, **kwargs):
        
        index = kwargs.pop("index", False)
        self.to_simpledataset().to_excel(
            excel_writer, sheet_name=sheet_name, index=index, **kwargs
        )
    """

    def to_dict(self):
        """Convert this :class:`DatasetFields` to a dictionary."""
        d = defaultdict(list)
        for dataset, field, _ in self.data:
            d[dataset].append(field)
        return d

    @classmethod
    def from_excel(cls, filepath, sheet_name) -> "DatasetFields":
        """Construct :class:`DatasetFields` from a :class:`pandas.DataFrame`."""
        instance = cls()
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0, index_col=None)
        df.apply(lambda x: instance.append_with_tags(x), axis="columns")
        return instance

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
