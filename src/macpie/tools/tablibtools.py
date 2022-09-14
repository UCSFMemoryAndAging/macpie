"""
Tablib is an format-agnostic tabular dataset library.
It allows you to import, export, and manipulate tabular data sets.
Advanced features include segregation, dynamic columns, tags & filtering,
and seamless format import & export.

"""

import openpyxl as pyxl
import pandas as pd
import tablib as tl

from macpie.tools import lltools, openpyxltools


class MacpieTablibDataset(tl.Dataset):
    """Extend :class:`tablib.Dataset` with extra functionality."""

    def __iter__(self):
        return (row for row in self.data)

    def __repr__(self) -> str:
        try:
            return (
                f"{self.__class__.__name__}("
                f"title={self.title!r}, "
                f"headers={self.headers!r}, "
                f"col_count={self.length!r}, "
                f"row_count={self.height!r})"
            )
        except AttributeError:
            return super().__repr__()

    @property
    def data(self):
        """Data of Dataset."""
        return self._data

    @property
    def df(self):
        """Get :class:`pandas.DataFrame` representation of data."""
        return self.export("df")

    def append_col_fill(self, fill_value, header=None):
        """Adds a column to the Dataset with a specified `fill_value`.

        Parameters
        ----------
        fill_value : str
            Value to fill new column with.
        header : str, Default is None
            Header for new column
        """

        fill_values = [fill_value] * self.height
        self.append_col(fill_values, header)

    def append_series(self, ser: pd.Series, with_tags: bool = True, tag_value: str = "x"):
        """Adds ``ser`` as a row to ``dset`` with tags derived
        from the labels in ``ser`` that are not headers in ``dset``,
        and whose value is ``'x'`` or ``'X'``.

        Parameters
        ----------
        dset : :class:`tablib.Dataset`
            The Dataset that gets ``ser`` appended to
        ser : :class:`pd.Series`
            A row of data to append to ``dset``

        Examples
        --------
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
        """

        ser = ser.copy()
        row = [ser.pop(item=header) for header in self.headers]

        if with_tags:
            tags = ser[ser.str.lower() == tag_value.lower()].index.tolist()
        else:
            tags = []

        self.append(row, tags=tags)

    def compare(self, other):
        """Compare this MacpieTablibDataset with another."""
        if self.headers != other.headers:
            raise ValueError("Can only compare datasets with matching headers.")

        if self.height != other.height:
            raise ValueError("Can only compare datasets with the same number of rows.")

        is_equal = True
        results = MacpieTablibDataset(headers=self.headers)
        for i, self_row in enumerate(self):
            results_row = []
            for j, self_col in enumerate(self_row):
                self_cell = self_col
                other_cell = other.data[i][j]
                if self_cell != other_cell:
                    is_equal = False
                    results_row.append(str(self_cell) + "|" + str(other_cell))
                elif j == 0:
                    results_row.append(self_cell)
                else:
                    results_row.append("")
            results.append(results_row)

        if is_equal:
            return None
        return results

    def extendleft(self, rows, tags=()):
        """Prepend a list of Dataset fields."""
        other_rows = [row for row in self]
        self.wipe_data()
        self.extend(rows, tags=tags)
        self.extend(other_rows)

    def to_excel(self, excel_writer):
        """Write to an excel file using an :class:`MACPieExcelWriter` instance."""
        excel_writer.write_tablib_dataset(self)

    def wipe_data(self):
        """Removes all content (but not headers)."""
        self._data = list()

    def print(self):
        """Print a representation table suited to a terminal in grid format."""
        print(self.export("cli", tablefmt="grid"))

    def subset(self, *args, **kwargs):
        rows = kwargs.pop("rows", None)
        cols = kwargs.pop("cols", None)
        if (rows is not None and list(rows) == []) or (cols is not None and list(cols) == []):
            # return empty dataset
            return MacpieTablibDataset(headers=self.headers, title=self.title)
        else:
            dset = super().subset(*args, rows=rows, cols=cols)
            if dset is None:
                # None is returned if no data
                return MacpieTablibDataset()
            return MacpieTablibDataset.from_tablib_dset(dset)

    @classmethod
    def from_df(cls, df, title: str = None) -> "MacpieTablibDataset":
        """Construct instance from a :class:`pandas.DataFrame`."""
        instance = cls(title=title)
        instance.dict = df.to_dict(orient="records")
        return instance

    @classmethod
    def from_excel(
        cls, filepath, sheet_name=None, headers=True, skip_lines=0, read_only=True
    ) -> "MacpieTablibDataset":
        """Construct instance from an Excel sheet."""
        return read_excel(
            filepath,
            sheet_name=sheet_name,
            headers=headers,
            skip_lines=skip_lines,
            read_only=read_only,
            tablib_class=cls,
        )

    @classmethod
    def from_tablib_dset(cls, dset, *args, **kwargs) -> "MacpieTablibDataset":
        instance = cls(headers=dset.headers, title=dset.title)
        instance._data = dset._data
        return instance


class DictLikeTablibDataset(MacpieTablibDataset):
    """Tabular representation of basic information using two columns
    only: a ``Key`` column and a ``Value`` column, using
    a :class:`macpie.tablibtools.MacpieTablibDataset`.

    It is a subclass of :class:`macpie.tablibtools.MacpieTablibDataset`, and therefore
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
    def from_dict(cls, dictionary, **kwargs) -> "DictLikeTablibDataset":
        """Construct :class:`DictLikeTablibDataset` from a Python dictionary."""
        tags = kwargs.pop("tags", [])
        instance = cls(**kwargs)
        instance.append_dict(dictionary, tags=tags)
        return instance


def filter_headers_pair(
    left: tl.Dataset,
    right: tl.Dataset,
    **kwargs,
):
    """
    Filter headers on a pair of Tablib Datasets.

    Parameters
    ----------
    left : :class:`tablib.Dataset`
    right : :class:`tablib.Dataset`
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`macpie.lltools.filter_seq_pair` to perform the filtering.

    Returns
    -------
    Tuple[Tuple[str, str], Tuple[str, str]]
        ((left_headers_kept, right_headers_kept), (left_headers_discarded, right_headers_discarded))
    """

    left_headers = left.headers
    right_headers = right.headers

    if not left_headers or not right_headers:
        return (left_headers, right_headers), ((), ())

    return lltools.filter_seq_pair(
        left_headers,
        right_headers,
        **kwargs,
    )


def read_excel(
    filepath, sheet_name=None, headers=True, skip_lines=0, read_only=True, tablib_class=tl.Dataset
):
    try:
        wb = pyxl.load_workbook(filepath, read_only=read_only, data_only=True)
        return openpyxltools.to_tablib_dataset(
            wb,
            sheet_name=sheet_name,
            headers=headers,
            skip_lines=skip_lines,
            tablib_class=tablib_class,
        )
    finally:
        if read_only:
            wb.close()


def subset_pair(
    left: tl.Dataset,
    right: tl.Dataset,
    **kwargs,
):
    """
    Subset columns of a pair of Tablib Datasets according to filtered headers.

    Parameters
    ----------
    left : :class:`tablib.Dataset`
    right : :class:`tablib.Dataset`
    **kwargs
        All remaining keyword arguments are passed through to the underlying
        :func:`filter_headers_pair` function to perform the filtering.

    Returns
    -------
    Tuple[Datset, Dataset]
        (subsetted left dataset, subsetted right dataset)
    """

    ((left_columns_to_keep, right_columns_to_keep), _) = filter_headers_pair(left, right, **kwargs)

    left = left.subset(cols=left_columns_to_keep)
    right = right.subset(cols=right_columns_to_keep)

    return (left, right)
