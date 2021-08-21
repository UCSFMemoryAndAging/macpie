from collections import namedtuple
from typing import ClassVar, List, Optional

import numpy as np
import pandas as pd
import tablib as tl

from macpie._config import get_option
from macpie.exceptions import DatasetIDColError, DatasetDateColError, DatasetID2ColError
from macpie.io.excel import MACPieExcelFormatter
from macpie.pandas.general import get_col_name, to_datetime
from macpie.tools import sequence as seqtools
from macpie.tools import string as strtools
from macpie.util.datasetfields import DatasetFields
from macpie.util.decorators import TrackHistory


DatasetKeyCols = namedtuple("DatasetKeyCols", "id_col, date_col, id2_col")


class Dataset:
    """The :class:`Dataset` object is the heart of MACPie.
    It represents two-dimensional tabular data with key fields commonly used in
    clinical research data: form ID, date of collection, and subject ID.

    :param df: The :class:`pandas.DataFrame` representing the actual
               data of this :class:`Dataset`.
    :param id_col: The column in ``df`` representing the primary key/index
                   of the :class:`Dataset`. Typically used for unique IDs of a clinical
                   research subject's data record (e.g. form, assessment, assay)
    :param date_col: The column in ``df`` representing the primary date column
                     of the :class:`Dataset`. Typically used for the date the data was collected.
    :param id2_col: The column in ``df`` representing the secondary key/index
                    of the :class:`Dataset`. Typically used for the ID of the subject themselves.
    :param name: The name of this :class:`Dataset`.
    :param tags: Arbitrary tags for the :class:`Dataset` that can be filtered on later.
                 Also used to create :attr:`Dataset.display_name`.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        id_col: str = None,
        date_col: str = None,
        id2_col: str = None,
        name: str = None,
        tags: List[str] = [],
    ):
        self._id_col = id_col

        self._date_col = date_col

        self._id2_col = id2_col

        self.name = name

        self.tags = tags

        self.display_name_generator = strtools.add_suffixes_with_base

        self.df = self._df_orig = df

    # -------------------------------------------------------------------------
    # Internals
    # -------------------------------------------------------------------------

    def __len__(self):
        return self.height

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"id_col={self._id_col!r}, "
            f"date_col={self._date_col!r}, "
            f"id2_col={self._id2_col!r}, "
            f"tags={self.tags!r})"
        )

    def _validate_df(self):
        if self._date_col is not None:
            try:
                self._date_col = to_datetime(self._df, self._date_col)
            except (KeyError, ValueError):
                raise DatasetDateColError(
                    f"Date column '{self._date_col}' in dataset '{self.name}' "
                    "could not be converted to native date objects"
                )

        if self._id2_col is not None:
            try:
                self._id2_col = get_col_name(self._df, self._id2_col)
            except KeyError:
                raise DatasetID2ColError(
                    f"ID2 column '{self._id2_col}' in dataset '{self.name}' not found"
                )

        if self._id_col is not None:
            try:
                self._id_col = get_col_name(self._df, self._id_col)
            except KeyError:
                raise DatasetIDColError(
                    f"ID column '{self._id_col}' in dataset '{self.name}' not found"
                )

            # if self._df[self._id_col].isnull().any():
            #    pass

            # from macpie.pandas.general import any_duplicates
            # if any_duplicates(self._df, self._id_col, ignore_nan=True):
            #    pass

    # -------------------------------------------------------------------------
    # Read-Only Properties
    # -------------------------------------------------------------------------

    @property
    def id_col(self):
        return self._id_col

    @property
    def date_col(self):
        return self._date_col

    @property
    def id2_col(self):
        return self._id2_col

    @property
    def display_name(self):
        """The name for this :class:`Dataset` suitable for display as generated by
        the :attr:`display_name_generator` function.
        """
        return self._display_name_generator(self.name, self.tags, max_length=-1, delimiter="_")

    @property
    def key_cols(self):
        """Returns list of non-null `key` column names of this :class:`Dataset`,
        defined as :attr:`id_col`, :attr:`date_col`, and :attr:`id2_col`
        """
        key_cols = []
        if self._id_col is not None:
            key_cols.append(self._id_col)
        if self._date_col is not None:
            key_cols.append(self._date_col)
        if self._id2_col is not None:
            key_cols.append(self._id2_col)
        return key_cols

    @property
    def sys_cols(self):
        """Returns list of `system` column names of this :class:`Dataset`,
        defined as any columns starting with ``column.system.prefix`` option.
        """

        sys_col_prefix = get_option("column.system.prefix")
        return [col for col in self.df.columns if col.startswith(sys_col_prefix)]

    @property
    def non_key_cols(self):
        """Returns list of `non-key` column names of this :class:`Dataset`,
        defined as any columns that are not :attr:`key_cols` or :attr:`sys_cols`.
        """
        key_and_sys_cols = self.key_cols + self.sys_cols
        return [col for col in self.df.columns if col not in key_and_sys_cols]

    @property
    def key_fields(self):
        """Returns list of all `key` fields of this :class:`Dataset`
        (analog of :attr:`key_cols`).
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [(self.name, col) for col in self.key_cols]

    @property
    def sys_fields(self):
        """Returns list of all `system` fields of this :class:`Dataset`
        (analog of :attr:`sys_cols`).
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [(self.name, col) for col in self.sys_cols]

    @property
    def non_key_fields(self):
        """Returns list of all `non-key` fields of this :class:`Dataset`
        (analog of :attr:`non_key_cols`).
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [(self.name, col) for col in self.non_key_cols]

    @property
    def all_fields(self):
        """Returns list of all fields of this :class:`Dataset`.
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [(self.name, col) for col in self.df.columns]

    @property
    def height(self):
        """The number of rows currently in the :class:`Dataset`."""
        return len(self._df.index)

    @property
    def width(self):
        """The number of columns currently in the :class:`Dataset`."""
        return len(self._df.columns)

    @property
    def history(self):
        """History information as generated by the
        :class:`macpie.util.TrackHistory` decorator.
        """
        if "_history" in self.__dict__:
            return self.__dict__["_history"]
        return []

    @property
    def df_orig(self):
        """Returns the original :class:`pandas.DataFrame` of this
        :class:`Dataset`. Useful if/when data is constantly modified.
        """
        return self._df_orig

    # -------------------------------------------------------------------------
    # Read/Write Properties
    # -------------------------------------------------------------------------

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        if value is None:
            raise ValueError("'df' cannot be None")
        if isinstance(value.columns, pd.MultiIndex):
            raise ValueError("'df' columns cannot be of type 'MultiIndex'")
        self._df = value
        self._validate_df()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        if value is None:
            self._tags = []
        else:
            self._tags = list(value)

    @property
    def display_name_generator(self):
        """The function used to generate :attr:`display_name`.
        The function should have the following input signature and
        will be passed the following parameters:

        :param arg1: :attr:`name`
        :param arg2: :attr:`tags`
        :param max_length: int denoting maximum length of the display name,
                           (-1 is default and denotes no limit)
        :param delimiter: string denoting a delimiter
                          ("_" is default)

        Defaults to :func:`macpie.strtools.add_suffixes_with_base`,
        which simply appends any tags to the :class:`Dataset` name.
        """
        return self._display_name_generator

    @display_name_generator.setter
    def display_name_generator(self, value):
        if callable(value):
            self._display_name_generator = value
        else:
            self._display_name_generator = lambda x: ""

    # -------------------------------------------------------------------------
    # Dataset DataFrame Methods
    # -------------------------------------------------------------------------

    def set_df(self, df, id_col=None, date_col=None, id2_col=None):
        if id_col:
            self._id_col = id_col
        if date_col:
            self._date_col = date_col
        if id2_col:
            self._id2_col = id2_col
        self.df = df

    # -------------------------------------------------------------------------
    # Tag Methods
    # -------------------------------------------------------------------------

    def add_tag(self, tag):
        """Add a tag to the :class:`Dataset`"""
        self._tags.append(tag)

    def clear_tags(self):
        """Clear all tags."""
        self._tags = []

    def replace_tag(self, old_tag, new_tag):
        """Replace ``old_tag`` with ``new_tag``."""
        if set(old_tag).issubset(set(self._tags)):
            old_tag = seqtools.maybe_make_list(old_tag)
            new_tag = seqtools.maybe_make_list(new_tag)
            for ot in old_tag:
                self._tags.remove(ot)
            self._tags.extend(new_tag)

    def has_tag(self, tag):
        """Returns true if :class:`Dataset` contains tag."""
        if tag is None:
            return False
        elif isinstance(tag, str):
            return tag in self._tags
        else:
            return bool(len(set(tag) & set(self._tags)))

    # -------------------------------------------------------------------------
    # Dataset Display Name Methods
    # -------------------------------------------------------------------------

    def get_excel_sheetname(self):
        """Generates a valid Excel sheet name by truncating
        :attr:`display_name` to 31 characters, the maximum allowed by Excel.
        """
        return self.display_name[:31]

    # -------------------------------------------------------------------------
    # Dataset Columns Methods
    # -------------------------------------------------------------------------

    def create_id_col(self, col_name="mp_id_col", start_index=1):
        """Create :attr:`id_col` with sequential numerical index.

        :param col_name: name of :attr:`id_col` to create
        :param start_index: index starting number

        """
        if self._id_col is not None:
            raise ValueError(f'"id_col" with value "{self._id_col}"" already exists')

        # self.sort_by_id2()
        # create an id_col called 'mp_id_col' with index starting from 1
        self._id_col = col_name
        self._df.insert(0, col_name, np.arange(start_index, len(self._df) + 1))

    def rename_id_col(self, new_id_col):
        """
        Rename :attr:`id_col` to ``new_id_col``
        """
        old_id_col = self._id_col
        self._id_col = new_id_col
        if old_id_col is not None and old_id_col in self._df.columns:
            self._df = self._df.rename(columns={old_id_col: new_id_col})

    def rename_col(self, old_col, new_col):
        """
        Rename ``old_col`` to ``new_col``. Note: ``old_col``
        cannot be a `key` column.
        """
        if old_col in self.non_key_cols or old_col in self.sys_cols:
            self._df = self._df.rename(columns={old_col: new_col})
        else:
            raise KeyError(f"Column '{old_col}' not in dataset or is a key column.")

    def drop_cols(self, cols):
        """Drop specified columns from :class:`Dataset`.

        :param cols: single label, or list-like

        """
        self._df = self._df.drop(columns=cols)

    def drop_sys_cols(self):
        """Drop all :attr:`sys_cols` from :class:`Dataset`."""
        self.drop_cols(self.sys_cols)

    def keep_cols(self, cols):
        """Keep specified columns (thus dropping the rest).
        Note: `Key` columns will always be kept.
        """
        cols_to_keep = self.key_cols

        # preserve order of the key columns by sorting them according
        # to existing order
        cols_to_keep.sort(key=lambda i: self._df.columns.tolist().index(i))

        cols = seqtools.maybe_make_list(cols)
        cols_to_keep.extend([c for c in cols if c not in cols_to_keep])
        self._df = self._df[cols_to_keep]

    def keep_fields(self, selected_fields: DatasetFields):
        """Keep specified fields (and drop the rest)."""
        if self.name in selected_fields.to_dict():
            self.keep_cols(selected_fields.to_dict()[self.name])

    # -------------------------------------------------------------------------
    # Sorting
    # -------------------------------------------------------------------------

    def sort_by_id2(self):
        """Sort :attr:`df` by :attr:`id2_col`."""

        sort_cols = []
        if self._id2_col:
            sort_cols.append(self._id2_col)
        if self._date_col:
            sort_cols.append(self._date_col)
        if self._id_col:
            sort_cols.append(self._id_col)
        if sort_cols:
            self._df = self._df.sort_values(by=sort_cols, na_position="last")

    # -------------------------------------------------------------------------
    # I/O Methods
    # -------------------------------------------------------------------------

    def to_dict(self):
        """Convert the :class:`Dataset` to a dictionary."""
        return {
            "name": self.name,
            "id_col": self._id_col,
            "date_col": self._date_col,
            "id2_col": self._id2_col,
            "tags": self.tags,
            "rows": self.height,
            "cols": self.width,
            "display_name": self.display_name,
            "excel_sheetname": self.get_excel_sheetname(),
        }

    def to_tablib(self):
        """Convert the :class:`Dataset` to a :class:`tablib.Dataset`."""
        tlset = tl.Dataset()
        tlset.title = self.display_name
        tlset.dict = [self.to_dict()]
        return tlset

    def to_excel(
        self,
        excel_writer,
        sheet_name: str = None,
        na_rep: str = "",
        float_format: Optional[str] = None,
        columns=None,
        header=True,
        index=False,
        index_label=None,
        startrow=0,
        startcol=0,
        engine=None,
        merge_cells=True,
        encoding=None,
        inf_rep="inf",
        verbose=True,
        freeze_panes=None,
        storage_options: pd._typing.StorageOptions = None,
    ) -> None:
        """Write :class:`Dataset` to an Excel sheet.

        As this is essentially writing the underlying :class:`pandas.DataFrame`
        (i.e. :attr:`df`) to Excel, this method mirrors :meth:`pandas.DataFrame.to_excel` with
        minor modifications. Whenever the `pandas` library is updated, this method
        should be checked to make sure it is still compatible.

        :param excel_writer: File path or existing ExcelWriter.
        :param sheet_name: Name of sheet which will contain Dataset, defaults to None
        :param na_rep: Missing data representation., defaults to ""
        :param float_format: Format string for floating point numbers. For example
                             ``float_format="%.2f"`` will format 0.1234 to 0.12., defaults to None
        :param columns: Columns to write, defaults to None
        :param header: Write out the column names. If a list of string is given it is
                       assumed to be aliases for the column names. Defaults to True
        :param index: Write row names (index). Defaults to False
        :param index_label: Column label for index column(s) if desired. If not specified, and
                            `header` and `index` are True, then the index names are used. A
                            sequence should be given if the DataFrame uses MultiIndex. Defaults to None
        :param startrow: Upper left cell row to dump data frame. Defaults to 0
        :param startcol: Upper left cell column to dump data frame. Defaults to 0
        :param engine: Write engine to use, 'openpyxl' or 'xlsxwriter'. Defaults to None
        :param merge_cells: Write MultiIndex and Hierarchical Rows as merged cells. Defaults to True
        :param encoding: Encoding of the resulting excel file. Only necessary for xlwt,
                         other writers support unicode natively. Defaults to None
        :param inf_rep: Representation for infinity (there is no native representation for
                        infinity in Excel). Defaults to "inf"
        :param verbose: Display more information in the error logs. Defaults to True
        :param freeze_panes: Specifies the one-based bottommost row and rightmost column that
                             is to be frozen. Defaults to None
        :param storage_options: Defaults to None
        """
        formatter = MACPieExcelFormatter(
            self,
            na_rep=na_rep,
            cols=columns,
            header=header,
            float_format=float_format,
            index=index,
            index_label=index_label,
            merge_cells=merge_cells,
            inf_rep=inf_rep,
        )
        formatter.write(
            excel_writer,
            sheet_name=sheet_name,
            startrow=startrow,
            startcol=startcol,
            freeze_panes=freeze_panes,
            engine=engine,
            storage_options=storage_options,
        )

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "Dataset":
        """
        Construct :class:`Dataset` from a file.
        """
        from macpie.pandas.io import file_to_dataframe

        df = file_to_dataframe(filepath)

        return cls(
            df,
            id_col=kwargs.get("id_col"),
            date_col=kwargs.get("date_col"),
            id2_col=kwargs.get("id2_col"),
            name=kwargs.get("name", filepath.stem),
            tags=kwargs.get("tags"),
        )

    @classmethod
    def from_excel_sheet(cls, filepath, dict_repr, id_dropna=False):
        """
        Construct :class:`Dataset` from a sheet within an Excel file.

        :param filepath: File path of Excel file.
        :param dict_repr: Dict representation of the :class:`Dataset`, i.e.,
            the return value of :meth:`to_dict()`.
        """
        dset_df = pd.read_excel(
            filepath, sheet_name=dict_repr["excel_sheetname"], index_col=None, header=0
        )

        if id_dropna:
            dset_df = dset_df.dropna(subset=[dict_repr["id_col"]])

        return cls(
            dset_df,
            id_col=dict_repr["id_col"],
            date_col=dict_repr["date_col"],
            id2_col=dict_repr["id2_col"],
            name=dict_repr["name"],
            tags=dict_repr["tags"],
        )

    # -------------------------------------------------------------------------
    # Data Transformation Methods
    # -------------------------------------------------------------------------

    @TrackHistory
    def date_proximity(
        self,
        anchor_dset: "Dataset",
        get: str = "all",
        when: str = "earlier_or_later",
        days: int = 90,
        dropna: bool = False,
        drop_duplicates: bool = False,
        duplicates_indicator: bool = False,
        merge_suffixes=get_option("operators.binary.column_suffixes"),
    ) -> None:
        """
        Links data across this :class:`Dataset` and ``anchor_dset``,
        updating :attr:`df` with the results.

        Calls :func:`macpie.date_proximity`, passing in ``anchor_dset`` as
        the "left" Dataset, and this Dataset as the "right" Dataset.
        """
        from macpie.core.reshape.date_proximity import date_proximity

        return date_proximity(
            left=anchor_dset,
            right=self,
            get=get,
            when=when,
            days=days,
            dropna=dropna,
            drop_duplicates=drop_duplicates,
            duplicates_indicator=duplicates_indicator,
            merge_suffixes=merge_suffixes,
        )

    @TrackHistory
    def group_by_keep_one(self, keep="all", drop_duplicates=False):
        """
        Links data across this :class:`Dataset` and ``anchor_dset``,
        updating :attr:`df` with the results.

        Calls :func:`macpie.date_proximity`, passing in ``anchor_dset`` as
        the "left" Dataset, and this Dataset as the "right" Dataset.
        """
        from macpie.core.reshape.group_by_keep_one import group_by_keep_one

        return group_by_keep_one(self, keep, drop_duplicates)


class LavaDataset(Dataset):

    FIELD_ID_COL_VALUE_DEFAULT: ClassVar[str] = "InstrID"
    FIELD_ID_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["INSTRID", "LINK_ID"]
    FIELD_ID2_COL_VALUE_DEFAULT: ClassVar[str] = "PIDN"
    FIELD_ID2_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["PIDN"]
    FIELD_DATE_COL_VALUE_DEFAULT: ClassVar[str] = "DCDate"
    FIELD_DATE_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["DATE", "DCDATE", "LINK_DATE"]

    def __init__(self, df: pd.DataFrame, **kwargs):
        super().__init__(
            df,
            id_col=kwargs.get("id_col", LavaDataset.FIELD_ID_COL_VALUE_DEFAULT),
            date_col=kwargs.get("date_col", LavaDataset.FIELD_DATE_COL_VALUE_DEFAULT),
            id2_col=kwargs.get("id2_col", LavaDataset.FIELD_ID2_COL_VALUE_DEFAULT),
            name=kwargs.get("name"),
            tags=kwargs.get("tags"),
        )

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "Dataset":
        """
        Construct LavaDataset from a file.
        """
        from macpie.pandas.io import file_to_dataframe

        df = file_to_dataframe(filepath)
        name = kwargs.pop("name", filepath.stem)
        return cls(df, name=name, **kwargs)
