import pandas as pd

from macpie._config import get_option
from macpie.tools import tablib as tablibtools


class DatasetFields(tablibtools.TablibWrapper):

    tag_key_field = 'key_field'
    tag_non_key_field = 'non_key_field'
    tag_sys_field = 'sys_field'

    def __init__(self, *args, **kwargs):
        self._col_dataset = get_option("column.dataset")
        self._col_field = get_option("column.field")

        headers = kwargs.pop('headers', (self._col_dataset, self._col_field))
        super().__init__(*args, headers=headers, **kwargs)

    def __repr__(self) -> str:
        try:
            return (
                f'{self.__class__.__name__}('
                f'title={self.title!r}, '
                f'datasets={self.datasets!r}, '
                f'total_fields={len(self)!r})'
            )
        except AttributeError:
            return self._tlset.__repr__()

    @property
    def datasets(self):
        return list(self.df[self._col_dataset].unique())

    def prepend(self, rows, tags=[]):
        other_rows = [row for row in self]
        self.wipe_data()
        self.extend(rows, tags=tags)
        self.extend(other_rows)

    def sort(self, collection):
        rows = [row for row in self]
        rows.sort(key=lambda i: collection.all_fields.index(i))
        self.wipe_data()
        self.extend(rows)

    def to_dict(self):
        dictionary = {}
        groups = self.df.groupby(by=self._col_dataset)
        for name, group in groups:
            dictionary[name] = group[self._col_field].tolist()
        return dictionary

    def to_excel(self, excel_writer, **kwargs):
        df = self.df
        sheet_name = kwargs.pop('sheet_name', self.title)
        index = kwargs.pop('index', False)
        df.to_excel(excel_writer, sheet_name=sheet_name, index=index, **kwargs)

    @classmethod
    def from_collection(cls, collection, **kwargs) -> "DatasetFields":
        """
        Construct DatasetFields from a MACPie Collection.
        """
        tags = kwargs.pop('tags', [])
        instance = cls(**kwargs)

        for dset in collection:
            if tags and not dset.has_tag(tags):
                continue
            for col in dset.df.columns:
                field = (dset.name, col)
                if field in collection.key_fields:
                    instance.append(field, tags=[DatasetFields.tag_key_field] + tags)
                elif field in collection.sys_fields:
                    instance.append(field, tags=[DatasetFields.tag_sys_field] + tags)
                else:
                    instance.append(field, tags=[DatasetFields.tag_non_key_field] + tags)

        return instance

    @classmethod
    def from_excel_sheet_create_tags(cls, filepath, sheet_name) -> "DatasetFields":
        """
        Construct DatasetFields from a pandas DataFrame.
        """
        instance = cls(title=sheet_name)
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0, index_col=None)
        df.apply(
            lambda x: tablibtools.append_with_tags(x, instance),
            axis='columns'
        )
        return instance
