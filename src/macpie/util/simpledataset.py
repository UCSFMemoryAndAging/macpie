from copy import copy
import json

import pandas as pd
import tablib as tl

from macpie import tablibtools


class SimpleDataset:
    """Wrap a :class:`tablib.Dataset` with extra functionality."""

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, "_tlset", tl.Dataset(*args, **kwargs))

    def __getattr__(self, attr):
        # override to proxy the wrapped object
        # this gets called when all other normal ways to supply attr fail
        # (e.g. __dict__, slots, properties),
        return getattr(self._tlset, attr)

    def __len__(self):
        return len(self._tlset)

    def __iter__(self):
        return (row for row in self.data)

    def __repr__(self) -> str:
        try:
            return (
                f"{self.__class__.__name__}("
                f"title={self._tlset.title!r}, "
                f"headers={self._tlset.headers!r}, "
                f"row_count={self._tlset.length!r}, "
                f"row_count={self._tlset.height!r})"
            )
        except AttributeError:
            return self._tlset.__repr__()

    @property
    def title(self):
        return self._tlset.title

    @title.setter
    def title(self, title):
        self._tlset.title = title

    @property
    def headers(self):
        return self._tlset.headers

    @headers.setter
    def headers(self, headers):
        self._tlset.headers = headers

    @property
    def data(self):
        return self._tlset._data

    @property
    def tlset(self):
        return self._tlset

    @property
    def df(self):
        """Get :class:`pandas.DataFrame` representation of data."""
        return self.tlset.export("df")

    def append_col_fill(self, fill_value, header=None):
        """Adds a column to the Dataset with a specified `fill_value`.

        :param fill_value: Value to fill new column with.
        :param header: Header for new column. Defaults to None.
        """
        fill_values = [fill_value] * self._tlset.height
        self.tlset.append_col(fill_values, header)

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
        row = [ser.pop(item=header) for header in self.headers]

        # dataset = ser.pop(item=self._col_header_dataset)
        # field = ser.pop(item=self._col_header_field)
        tags = ser[ser.str.lower() == tag_value.lower()].index.tolist()
        self.append(row, tags=tags)

    def extendleft(self, rows, tags=()):
        """Prepend a list of Dataset fields."""
        other_rows = [row for row in self]
        self.wipe_data()
        self.extend(rows, tags=tags)
        self.extend(other_rows)

    def filter(self, tag):
        """Returns a new instance, excluding any rows that
        do not contain the given tag.
        """
        return self.from_tlset(self.tlset.filter(tag))

    def to_excel(self, excel_writer):
        excel_writer.write_tablib_dataset(self.tlset)

    def wipe_data(self):
        """Removes all content (but not headers)."""
        self.tlset._data = list()

    def print(self):
        """Print a representation table suited to a terminal in grid format."""
        print(self.export("cli", tablefmt="grid"))

    @classmethod
    def from_df(cls, df, title: str = None) -> "SimpleDataset":
        """Construct instance from a :class:`pandas.DataFrame`."""
        instance = cls(title=title)
        instance.tlset.dict = df.to_dict(orient="records")

        return instance

    @classmethod
    def from_tlset(
        cls,
        tlset,
    ) -> "SimpleDataset":
        """Construct instance from a :class:`tablib.Dataset`."""
        instance = cls()
        instance._tlset = tlset

        return instance

    @classmethod
    def from_excel(cls, filepath, sheet_name) -> "SimpleDataset":
        """Construct instance from an Excel sheet."""
        loaded_tlset = tablibtools.read_excel(filepath, sheet_name)
        loaded_tlset.title = sheet_name

        instance = cls()
        instance._tlset = loaded_tlset

        return instance


class DictLikeDataset(SimpleDataset):
    """Tabular representation of basic information using two columns
    only: a ``Key`` column and a ``Value`` column, using
    a :class:`macpie.tablibtools.SimpleDataset`.

    All ``Value``'s are encoded as JSON. But you can call the ``to_dict()`` method
    to decode the JSON back to native Python objects.

    It is a subclass of :class:`macpie.tablibtools.SimpleDataset`, and therefore
    can be initialized with data the same way.
    """

    _col_header_key = "Key"
    _col_header_value = "Value"

    def __init__(self, *args, **kwargs):
        headers = kwargs.pop("headers", (self._col_header_key, self._col_header_value))
        super().__init__(*args, headers=headers, **kwargs)

    def append_dict(self, dictionary, tags=()):
        """Add a dictionary of items.

        :param dictionary: Dict to add
        :param tags: tags to add to dict items
        """
        for k, v in dictionary.items():
            self.append((k, v), tags=tags)

    def to_dict(self):
        """Convert to native dict for easy reading/access."""
        # convert to a native dict for easy reading
        return dict(self.data)

    @classmethod
    def from_dict(cls, dictionary, **kwargs) -> "DictLikeDataset":
        """Construct :class:`Info` from a Python dictionary."""
        tags = kwargs.pop("tags", [])
        instance = cls(**kwargs)
        instance.append_dict(dictionary, tags=tags)
        return instance
