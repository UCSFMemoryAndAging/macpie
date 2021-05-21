from openpyxl import load_workbook
import pandas as pd
import tablib as tl


class TablibWrapper:
    """Wrap a :class:`tablib.Dataset` with extra functionality.
    """

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, '_tlset', tl.Dataset(*args, **kwargs))

    def __getattr__(self, attr):
        # override to proxy the wrapped object
        # this gets called when all other normal ways to supply attr fail
        # (e.g. __dict__, slots, properties),
        return getattr(self._tlset, attr)

    def __len__(self):
        return len(self._tlset)

    def __iter__(self):
        return (row for row in self._tlset)

    def __repr__(self) -> str:
        try:
            return (
                f'{self.__class__.__name__}('
                f'title={self._tlset.title!r}, '
                f'headers={self._tlset.headers!r}, '
                f'num_rows={len(self._tlset)!r})'
            )
        except AttributeError:
            return self._tlset.__repr__()

    @property
    def df(self):
        """Get :class:`pandas.DataFrame` representation of data.
        """
        return self._tlset.export('df')

    def append_col_fill(self, fill_value, header=None):
        """Adds a column to the Dataset with a specified `fill_value`.

        :param fill_value: Value to fill new column with.
        :param header: Header for new column. Defaults to None.
        """
        fill_values = [fill_value] * self._tlset.height
        self._tlset.append_col(fill_values, header)

    def filter(self, tag):
        """Returns a new instance, excluding any rows that
        do not contain the given tag.
        """
        return self.from_tlset(self._tlset.filter(tag))

    def to_excel(self, excel_writer, **kwargs):
        excel_writer.write_tlset(self._tlset, **kwargs)

    def wipe_data(self):
        """Removes all content (but not headers).
        """
        self._tlset._data = list()

    def print(self):
        """Print a representation table suited to a terminal in grid format.
        """
        print(self.export("cli", tablefmt="grid"))

    @classmethod
    def from_df(cls, df, title: str = None) -> "TablibWrapper":
        """Construct instance from a :class:`pandas.DataFrame`.
        """
        instance = cls(title=title)
        instance._tlset.dict = df.to_dict(orient='records')

        return instance

    @classmethod
    def from_tlset(cls, tlset, title: str = None) -> "TablibWrapper":
        """Construct instance from a :class:`tablib.Dataset`.
        """
        if title:
            tlset.title = title

        instance = cls()
        instance._tlset = tlset

        return instance

    @classmethod
    def from_excel_sheet(cls, filepath, sheet_name) -> "TablibWrapper":
        """Construct instance from an Excel sheet.
        """
        loaded_tlset = excel_to_tablib(filepath, sheet_name)
        loaded_tlset.title = sheet_name

        instance = cls()
        instance._tlset = loaded_tlset

        return instance


def append_with_tags(dset: tl.Dataset, ser: pd.Series):
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
    headers = dset.headers
    data_row = [ser.pop(item=header) for header in headers]
    tags = ser[ser.str.lower() == 'x'].index.tolist()
    dset.append(data_row, tags)


def excel_to_tablib(filepath, sheet_name: str = None, headers=True):
    """Returns a Tablib Dataset from an Excel file.
    """

    wb = load_workbook(filepath, read_only=True, data_only=True)
    sheet = wb.active if sheet_name is None else wb[sheet_name]

    dset = tl.Dataset()
    dset.title = sheet.title

    for i, row in enumerate(sheet.rows):
        row_vals = [c.value for c in row]
        if (i == 0) and (headers):
            dset.headers = row_vals
        else:
            dset.append(row_vals)

    return dset
