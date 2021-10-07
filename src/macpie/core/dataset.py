import json
from typing import ClassVar, List
from macpie.util.simpledataset import DictLikeDataset

import numpy as np
import pandas as pd
from pandas.core.dtypes.generic import ABCDataFrame

from macpie._config import get_option
from macpie.io.excel import safe_xlsx_sheet_title, MACPieExcelFile
from macpie.pandas.general import get_col_name, is_date_col, to_datetime
from macpie.tools import sequence as seqtools
from macpie.tools import string as strtools
from macpie.util.decorators import TrackHistory

from .datasetfields import DatasetField

DEFAULT_ID_COL_NAME = "PIDN"
DEFAULT_DATE_COL_NAME = "DCDate"
DEFAULT_ID2_COL_NAME = "InstrID"

DEFAULT_NAME = "NO_NAME"


class Dataset(pd.DataFrame):

    _metadata = [
        "_id_col_name",
        "_date_col_name",
        "_id2_col_name",
        "_name",
        "_tags",
        "_display_name_generator",
        "_history",
    ]

    # _id_col_name = DEFAULT_ID_COL_NAME
    # _date_column_name = DEFAULT_DATE_COL_NAME
    # _id2_column_name = DEFAULT_ID2_COL_NAME

    def __init__(
        self,
        data=None,
        *args,
        id_col_name=None,
        date_col_name=None,
        id2_col_name=None,
        name=None,
        tags=None,
        display_name_generator=None,
        id_col_dropna=False,
        **kwargs,
    ):
        super().__init__(data, *args, **kwargs)

        self.id_col_name = id_col_name
        self.date_col_name = date_col_name
        self.id2_col_name = id2_col_name
        self.name = name
        self.tags = tags
        self.display_name_generator = display_name_generator

        if id_col_dropna:
            self.dropna(subset=["id_col_name"], inplace=True)

    def __setattr__(self, attr, val):
        # Have to special case tags b/c pandas tries to use as column.
        # Specifically, avoids the the following warning:
        # UserWarning: Pandas doesn't allow columns to be created via a new attribute name -
        # see https://pandas.pydata.org/pandas-docs/stable/indexing.html#attribute-access
        if attr in ("id_col_name", "date_col_name", "id2_col_name", "tags"):
            object.__setattr__(self, attr, val)
        else:
            super().__setattr__(attr, val)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"id_col_name={self.id_col_name!r}, "
            f"date_col_name={self.date_col_name!r}, "
            f"id2_col_name={self.id2_col_name!r}, "
            f"name={self.name!r}, "
            f"tags={self.tags!r}, "
            f"df=\n{super().__repr__()}\n)"
        )

    @property
    def row_count(self):
        """The number of rows currently in the :class:`Dataset`."""
        return len(self.index)

    @property
    def col_count(self):
        """The number of columns currently in the :class:`Dataset`."""
        return len(self.columns)

    def equals(self, other: object):
        if isinstance(other, Dataset):
            if self.name != other.name or self.tags != other.tags:
                return False
        return super().equals(other)

    @property
    def id_col_name(self):
        if self._id_col_name and self._id_col_name not in self.columns:
            raise AttributeError(f"No id column found: '{self._id_col_name}'.")
        return self._id_col_name

    @id_col_name.setter
    def id_col_name(self, val):
        if val is not None:
            try:
                self._id_col_name = get_col_name(self, val)
            except KeyError:
                raise ValueError(f"Unknown column '{val}'")
            except Exception:
                raise
        else:
            self._id_col_name = None

    @property
    def date_col_name(self):
        if self._date_col_name and self._date_col_name not in self.columns:
            raise AttributeError(f"No date column found: '{self._date_col_name}'.")
        return self._date_col_name

    @date_col_name.setter
    def date_col_name(self, val):
        if val is not None:
            try:
                self._date_col_name = get_col_name(self, val)
                to_datetime(self, self._date_col_name)
            except KeyError:
                raise ValueError(f"Unknown column '{val}'")
            except Exception:
                raise
        else:
            self._date_col_name = None

    @property
    def id2_col_name(self):
        if self._id2_col_name and self._id2_col_name not in self.columns:
            raise AttributeError(f"No id2 column found: '{self._id2_col_name}'.")
        return self._id2_col_name

    @id2_col_name.setter
    def id2_col_name(self, val):
        if val is not None:
            try:
                self._id2_col_name = get_col_name(self, val)
            except KeyError:
                raise ValueError(f"Unknown column '{val}'")
            except Exception:
                raise
        else:
            self._id2_col_name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        if val is None:
            self._name = DEFAULT_NAME
        else:
            self._name = val

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, val):
        if val is None:
            self._tags = []
        else:
            self._tags = list(val)

    @property
    def display_name(self):
        """The name for this :class:`Dataset` suitable for display as generated by
        the :attr:`display_name_generator` function.
        """
        return self._display_name_generator(self)

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
    def display_name_generator(self, val):
        if callable(val):
            self._display_name_generator = val
        else:
            self._display_name_generator = self.default_display_name_generator

    @property
    def history(self):
        """History information as generated by the
        :class:`macpie.util.TrackHistory` decorator.
        """
        if "_history" in self.__dict__:
            return self.__dict__["_history"]
        return []

    @property
    def _constructor(self):
        return Dataset

    @staticmethod
    def default_display_name_generator(dset):
        return strtools.add_suffixes_with_base(dset.name, dset.tags, max_length=-1, delimiter="_")

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
        :attr:`display_name` to 30 characters. The maximum allowed by Excel is 31,
        but leaving one character for use by library (i.e. prepending an '_').
        """
        return safe_xlsx_sheet_title(self.display_name[:31], "-")

    # -------------------------------------------------------------------------
    # Column and Field Properties
    # -------------------------------------------------------------------------

    @property
    def key_cols(self):
        """Returns list of non-null `key` column names of this :class:`Dataset`,
        defined as :attr:`id_col_name`, :attr:`date_col_name`, and :attr:`id2_col_name`
        """
        key_cols = []
        if self._id_col_name is not None:
            key_cols.append(self._id_col_name)
        if self._date_col_name is not None:
            key_cols.append(self._date_col_name)
        if self._id2_col_name is not None:
            key_cols.append(self._id2_col_name)
        return key_cols

    @property
    def sys_cols(self):
        """Returns list of `system` column names of this :class:`Dataset`,
        defined as any columns starting with ``column.system.prefix`` option.
        """
        sys_col_prefix = get_option("column.system.prefix")
        return [col for col in self.columns if col.startswith(sys_col_prefix)]

    @property
    def non_key_cols(self):
        """Returns list of `non-key` column names of this :class:`Dataset`,
        defined as any columns that are not :attr:`key_cols` or :attr:`sys_cols`.
        """
        key_and_sys_cols = self.key_cols + self.sys_cols
        return [col for col in self.columns if col not in key_and_sys_cols]

    @property
    def key_fields(self):
        """Returns list of all `key` fields of this :class:`Dataset`
        (analog of :attr:`key_cols`).
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [DatasetField(self.name, col) for col in self.key_cols]

    @property
    def sys_fields(self):
        """Returns list of all `system` fields of this :class:`Dataset`
        (analog of :attr:`sys_cols`).
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [DatasetField(self.name, col) for col in self.sys_cols]

    @property
    def non_key_fields(self):
        """Returns list of all `non-key` fields of this :class:`Dataset`
        (analog of :attr:`non_key_cols`).
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [DatasetField(self.name, col) for col in self.non_key_cols]

    @property
    def all_fields(self):
        """Returns list of all fields of this :class:`Dataset`.
        A field is a (:attr:`name`, ``col_name``) tuple, where
        ``col_name`` is a column header in :attr:`df`.
        """
        return [DatasetField(self.name, col) for col in self.columns]

    def create_id_col(self, col_name="mp_id_col", start_index=1):
        """Create :attr:`id_col_name` with sequential numerical index.

        :param col_name: name of :attr:`id_col_name` to create
        :param start_index: index starting number

        """
        if self._id_col_name is not None:
            raise ValueError(f'"id_col_name" with value "{self._id_col_name}"" already exists')

        # self.sort_by_id2()
        # create an id_col_name called 'mp_id_col' with index starting from 1
        self._id_col_name = col_name
        self.insert(0, col_name, np.arange(start_index, len(self) + 1))

    # -------------------------------------------------------------------------
    # Sorting
    # -------------------------------------------------------------------------

    def sort_by_id2(self):
        """Sort :attr:`df` by :attr:`id2_col_name`."""
        sort_cols = list(reversed(self.key_cols))
        if sort_cols:
            return self.sort_values(by=sort_cols, na_position="last")
        return self

    # -------------------------------------------------------------------------
    # I/O Methods
    # -------------------------------------------------------------------------

    def to_excel_dict(self):
        """Convert the :class:`Dataset` to a dictionary."""
        return {
            "class_name": self.__class__.__name__,
            "id_col_name": self._id_col_name,
            "date_col_name": self._date_col_name,
            "id2_col_name": self._id2_col_name,
            "name": self.name,
            "display_name": self.display_name,
            "excel_sheetname": self.get_excel_sheetname(),
            "tags": self.tags,
            "row_count": self.row_count,
            "col_count": self.col_count,
        }

    @classmethod
    def from_excel_dict(cls, excel_dict, df):
        return Dataset(
            data=df,
            id_col_name=excel_dict.get("id_col_name"),
            date_col_name=excel_dict.get("date_col_name"),
            id2_col_name=excel_dict.get("id2_col_name"),
            name=excel_dict.get("name"),
            tags=excel_dict.get("tags"),
        )

    def get_excel_repr(self):
        return DictLikeDataset(
            *[(self.get_excel_sheetname(), self.to_excel_dict())],
            title=MACPieExcelFile._datasets_sheet_name,
        )

    def to_excel(self, excel_writer, write_repr=True, **kwargs) -> None:
        """Write :class:`Dataset` to an Excel sheet.

        :param excel_writer: File path or existing ExcelWriter.
        :param kwargs:
        """
        from macpie import MACPieExcelWriter

        if isinstance(excel_writer, MACPieExcelWriter):
            need_save = False
        else:
            excel_writer = MACPieExcelWriter(
                excel_writer, engine="openpyxl", storage_options=kwargs.get("storage_options")
            )
            need_save = True

        try:
            if isinstance(self.index, pd.MultiIndex) or isinstance(self.columns, pd.MultiIndex):
                index = kwargs.pop("index", True)
            else:
                index = kwargs.pop("index", False)

            sheet_name = kwargs.pop("sheet_name", self.get_excel_sheetname())
            super().to_excel(excel_writer, sheet_name=sheet_name, index=index, **kwargs)

            if write_repr:
                self.get_excel_repr().to_excel(excel_writer)
        finally:
            # make sure to close opened file handles
            if need_save:
                excel_writer.close()

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "Dataset":
        """
        Construct :class:`Dataset` from a file.
        """
        from macpie.pandas.io import file_to_dataframe

        df = file_to_dataframe(filepath)

        return cls(
            data=df,
            id_col_name=kwargs.get("id_col_name"),
            date_col_name=kwargs.get("date_col_name"),
            id2_col_name=kwargs.get("id2_col_name"),
            name=kwargs.get("name", filepath.stem),
            tags=kwargs.get("tags"),
        )

    # -------------------------------------------------------------------------
    # Data Transformation Methods
    # -------------------------------------------------------------------------

    @TrackHistory
    def date_proximity(
        self,
        right_dset: "Dataset",
        get: str = "all",
        when: str = "earlier_or_later",
        days: int = 90,
        dropna: bool = False,
        drop_duplicates: bool = False,
        duplicates_indicator: bool = False,
        merge_suffixes=get_option("operators.binary.column_suffixes"),
        prepend_level_name: bool = True,
    ) -> None:
        """
        Links data across this :class:`Dataset` and ``right_dset``,
        updating :attr:`df` with the results.

        Calls :func:`macpie.date_proximity`, passing in ``right_dset`` as
        the "left" Dataset, and this Dataset as the "right" Dataset.
        """
        from macpie.core.operators.date_proximity import date_proximity

        return date_proximity(
            left=self,
            right=right_dset,
            get=get,
            when=when,
            days=days,
            dropna=dropna,
            drop_duplicates=drop_duplicates,
            duplicates_indicator=duplicates_indicator,
            merge_suffixes=merge_suffixes,
            prepend_level_name=prepend_level_name,
        )

    @TrackHistory
    def group_by_keep_one(self, keep="all", drop_duplicates=False):
        """ """
        from macpie.core.operators.group_by_keep_one import group_by_keep_one

        return group_by_keep_one(self, keep, drop_duplicates)


class LavaDataset(Dataset):

    FIELD_ID_COL_VALUE_DEFAULT: ClassVar[str] = "InstrID"
    FIELD_ID_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["INSTRID", "LINK_ID"]
    FIELD_ID2_COL_VALUE_DEFAULT: ClassVar[str] = "PIDN"
    FIELD_ID2_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["PIDN"]
    FIELD_DATE_COL_VALUE_DEFAULT: ClassVar[str] = "DCDate"
    FIELD_DATE_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["DATE", "DCDATE", "LINK_DATE"]

    def __init__(self, *args, **kwargs):
        id_col_name = kwargs.pop("id_col_name", LavaDataset.FIELD_ID_COL_VALUE_DEFAULT)
        date_col_name = kwargs.pop("date_col_name", LavaDataset.FIELD_DATE_COL_VALUE_DEFAULT)
        id2_col_name = kwargs.pop("id2_col_name", LavaDataset.FIELD_ID2_COL_VALUE_DEFAULT)

        super().__init__(
            *args,
            id_col_name=id_col_name,
            date_col_name=date_col_name,
            id2_col_name=id2_col_name,
            **kwargs,
        )

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "LavaDataset":
        """
        Construct LavaDataset from a file.
        """
        from macpie.pandas.io import file_to_dataframe

        df = file_to_dataframe(filepath)
        name = kwargs.pop("name", filepath.stem)
        return cls(data=df, name=name, **kwargs)