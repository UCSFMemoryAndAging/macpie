from typing import ClassVar, List

import numpy as np
import pandas as pd

from macpie._config import get_option
from macpie.core.datasetfields import DatasetField, DatasetFields

# from macpie.core.macseries import MacSeries
from macpie.pandas.select import get_col_name
from macpie.tools import itertools, lltools, strtools
from macpie.util.decorators.method import MethodHistory


class Dataset(pd.DataFrame):
    """
    A Dataset object is a pandas.DataFrame that has columns representing
    common data associated with clinical research assessments. In addition
    to the standard DataFrame constructor arguments, Dataset also accepts
    the following keyword arguments:

    Parameters
    ----------
    id_col_name : str (optional)
        Column to use as record IDs.
    date_col_name : str (optional)
        Column to use as record collection date.
    date_col_errors : {'ignore', 'raise', 'coerce'}, default 'raise'
        - If :const:`'raise'`, then invalid parsing will raise an exception.
        - If :const:`'coerce'`, then invalid parsing will be set as :const:`NaT`.
        - If :const:`'ignore'`, then invalid parsing will return the input.
    id2_col_name : str (optional)
        Column to use as secondary IDs, most commonly patient/subject IDs.
    name : str (optional)
        Name of the Dataset.
    tags : str or sequence of strs
        Associate tags with this Dataset to enable filtering later on.
    display_name_generator : function
        A function that accepts a single Dataset parameter and returns
        a string to be used as :attr:`display_name`.

    Examples
    --------
    Constructing Dataset from a dictionary.

    >>> d = {"pidn": [1, 2], "dcdate": ["1/1/2001", "2/2/2002"], "cdr": [1.0, 1.5]}
    >>> dset = mp.Dataset(d, id_col_name="pidn", date_col_name="dcdate")
    >>> dset
    Dataset(id_col_name='pidn', date_col_name='dcdate', id2_col_name=None, name='NO_NAME', tags=[], data=
       pidn     dcdate  cdr
    0     1 2001-01-01  1.0
    1     2 2002-02-02  1.5
    )

    Notice that the ``date_col_name`` column has been converted to a
    ``datetime`` column. Errors raised trying to convert the column
    are controlled by :py:attr:`date_col_errors`.

    >>> dset.dtypes
    pidn               int64
    dcdate    datetime64[ns]
    cdr              float64
    dtype: object
    """

    _metadata = [
        "_id_col_name",
        "_date_col_errors",
        "_date_col_name",
        "_id2_col_name",
        "_name",
        "_tags",
        "_display_name_generator",
    ]

    #: Tag that denotes this Dataset has duplicates
    tag_duplicates = "duplicates"

    def __init__(
        self,
        data=None,
        *args,
        id_col_name=None,
        date_col_errors="raise",
        date_col_name=None,
        id2_col_name=None,
        name=None,
        tags=None,
        display_name_generator=None,
        **kwargs,
    ):
        super().__init__(data, *args, **kwargs)

        self.id_col_name = id_col_name
        self.date_col_errors = date_col_errors
        self.date_col_name = date_col_name
        self.id2_col_name = id2_col_name
        self.name = name if name else get_option("dataset.default.name")
        self.tags = tags

        self.display_name_generator = (
            display_name_generator
            if display_name_generator
            else self.default_display_name_generator
        )

    def __setattr__(self, attr, val):
        # Have to special case tags b/c pandas tries to use as column.
        # Specifically, avoids the the following warning:
        # UserWarning: Pandas doesn't allow columns to be created via a new attribute name -
        # see https://pandas.pydata.org/pandas-docs/stable/indexing.html#attribute-access
        if attr in ("id_col_name", "date_col_name", "id2_col_name", "tags", "_method_history"):
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
            f"data=\n{super().__repr__()}\n)"
        )

    __hash__ = object.__hash__

    @property
    def row_count(self):
        """Number of rows in :class:`Dataset`."""
        return len(self.index)

    @property
    def col_count(self):
        """Number of columns in :class:`Dataset`."""
        return len(self.columns)

    @property
    def id_col_name(self):
        """Column to use as record IDs."""
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
    def date_col_errors(self):
        """Errors flag to use when parsing :attr:`date_col_name`"""
        return self._date_col_errors

    @date_col_errors.setter
    def date_col_errors(self, val):
        self._date_col_errors = val

    @property
    def date_col_name(self):
        """Column to use as record collection date."""
        if self._date_col_name and self._date_col_name not in self.columns:
            raise AttributeError(f"No date column found: '{self._date_col_name}'.")
        return self._date_col_name

    @date_col_name.setter
    def date_col_name(self, val):
        if val is not None:
            try:
                self._date_col_name = get_col_name(self, val)
                if not self.mac.is_date_col(self._date_col_name):
                    self[self._date_col_name] = pd.to_datetime(
                        self[self._date_col_name], errors=self._date_col_errors
                    )
            except KeyError:
                raise ValueError(f"Unknown column '{val}'")
            except Exception:
                raise
        else:
            self._date_col_name = None

    @property
    def id2_col_name(self):
        """Column to use as secondary record IDs."""
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
        """Name of Dataset."""
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def tags(self):
        """Tag(s) of Dataset."""
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

        Parameters
        ----------
        arg1: str
            :attr:`Dataset.name`
        arg2: str or list of str
            :attr:`Dataset.tags`
        max_length : int, Default is -1 (meaning no limit)
            Maximum length of the display name
        delimiter : str, Default is "_"
            Delimiter to use to separate tags.

        Notes
        -----
        Defaults to :func:`macpie.strtools.add_suffixes_with_base`,
        which simply appends any tags to the :class:`Dataset` name.
        """
        return self._display_name_generator

    @display_name_generator.setter
    def display_name_generator(self, val):
        if not callable(val):
            raise ValueError("display_name_generator must be a callable type")

        self._display_name_generator = val

    @property
    def history(self):
        """History information as generated by the
        :class:`macpie.util.MethodHistory` decorator.
        """
        if "_method_history" in self.__dict__:
            return self._method_history
        return []

    @staticmethod
    def default_display_name_generator(dset):
        """Default function to use as :attr:`display_name_generator`. It
        appends any tags to :attr:`name`."""
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
            old_tag = lltools.maybe_make_list(old_tag)
            new_tag = lltools.maybe_make_list(new_tag)
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

    @property
    def excel_sheetname(self):
        """Generates a valid Excel sheet name by truncating
        :attr:`display_name` to 30 characters. The maximum allowed by Excel is 31,
        but leaving one character for use by library (i.e. prepending an '_').
        """
        from macpie.io.excel import safe_xlsx_sheet_title

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

        if isinstance(self.columns, pd.MultiIndex):
            return [col for col in self.columns if col[-1].startswith(sys_col_prefix)]
        else:
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

        Parameters
        ----------
        col_name : str
            Name of :attr:`id_col_name` to create
        start_index : int
            Index starting number
        """
        if self._id_col_name is not None:
            raise ValueError(f'"id_col_name" with value "{self._id_col_name}"" already exists')

        # self.sort_by_id2()
        # create an id_col_name called 'mp_id_col' with index starting from 1
        self._id_col_name = col_name
        self.insert(0, col_name, np.arange(start_index, len(self) + 1))

    def rename_col(self, old_col, new_col, inplace=False):
        """
        Rename ``old_col`` to ``new_col``. Note: ``old_col``
        cannot be a `key` column.
        """
        if old_col in self.non_key_cols or old_col in self.sys_cols:
            return super().rename(columns={old_col: new_col}, inplace=inplace)
        else:
            raise KeyError(f"Column '{old_col}' not in dataset or is a key column.")

    def prepend_level(self, level, inplace=False):
        """Create a ``MultiIndex`` by adding level as the first level."""
        if isinstance(self.columns, pd.MultiIndex):
            raise NotImplementedError("Dataset already has multiple levels.")

        if inplace:
            dset = self
        else:
            dset = self.copy()

        dset.columns = pd.MultiIndex.from_product([[level], dset.columns])
        dset._id_col_name = (level, dset._id_col_name) if dset._id_col_name else None
        dset._date_col_name = (level, dset._date_col_name) if dset._date_col_name else None
        dset._id2_col_name = (level, dset._id2_col_name) if dset._id2_col_name else None

        if not inplace:
            return dset

    def drop_sys_cols(self, inplace=False):
        """Drop all :attr:`sys_cols` from :class:`Dataset`."""
        return self.drop(columns=self.sys_cols, inplace=inplace)

    def keep_cols(self, cols, inplace=False):
        """Keep specified columns (thus dropping the rest).
        Note: `Key` columns will always be kept.
        """
        cols_to_keep = self.key_cols

        # preserve order of the key columns by sorting them according
        # to existing order
        cols_to_keep.sort(key=lambda i: self.columns.tolist().index(i))

        cols = lltools.maybe_make_list(cols)
        cols_to_keep.extend([c for c in cols if c not in cols_to_keep])

        result = self[cols_to_keep]
        if inplace:
            return self._update_inplace(result)
        else:
            return result

    def keep_fields(self, selected_fields: DatasetFields, inplace=False):
        """Keep specified fields (and drop the rest)."""
        if self.name in selected_fields.unique_datasets:
            if inplace:
                self.keep_cols(selected_fields.to_dict()[self.name], inplace=True)
            else:
                return self.keep_cols(selected_fields.to_dict()[self.name], inplace=False)

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
        """
        Convert the :class:`Dataset` to a dictionary representation needed
        for Excel reading/writing.

        Returns
        -------
        dict
        """

        return {
            "class_name": self.__class__.__name__,
            "id_col_name": self._id_col_name,
            "date_col_name": self._date_col_name,
            "id2_col_name": self._id2_col_name,
            "name": self.name,
            "display_name": self.display_name,
            "excel_sheetname": self.excel_sheetname,
            "tags": self.tags,
            "row_count": self.row_count,
            "col_count": self.col_count,
        }

    @classmethod
    def from_excel_dict(cls, excel_dict, df):
        """
        Construct a Dataset from a dictionary representation.

        Parameters
        ----------
        excel_dict : dict
            The dictionary generated from :meth:`to_excel_dict`
        df : DataFrame
            The DataFrame containing the data.
        """

        return Dataset(
            data=df,
            id_col_name=excel_dict.get("id_col_name"),
            date_col_name=excel_dict.get("date_col_name"),
            id2_col_name=excel_dict.get("id2_col_name"),
            name=excel_dict.get("name"),
            tags=excel_dict.get("tags"),
        )

    @staticmethod
    def excel_dict_has_tags(excel_dict, tags):
        """Helper function to determine if an ``excel_dict`` has ``tags``."""
        excel_dict_tags = excel_dict["tags"]
        if tags is None:
            return False
        elif isinstance(tags, str):
            return tags in excel_dict_tags
        else:
            return bool(len(set(tags) & set(excel_dict_tags)))

    def cross_section(self, excel_dict):
        """Return the Dataset defined by ``excel_dict`` from this Dataset."""
        if not isinstance(self.columns, pd.MultiIndex):
            raise NotImplementedError

        df = self.xs(excel_dict["name"], axis="columns", level=0)
        dset = Dataset(
            df,
            id_col_name=excel_dict["id_col_name"],
            date_col_name=excel_dict["date_col_name"],
            id2_col_name=excel_dict["id2_col_name"],
            name=excel_dict["name"],
        )
        dset.drop_sys_cols()
        return dset

    def to_excel(
        self,
        excel_writer,
        sheet_name=None,
        na_rep="",
        float_format=None,
        columns=None,
        header=True,
        index=False,
        index_label=None,
        startrow=0,
        startcol=0,
        engine=None,
        inf_rep="inf",
        merge_cells=True,
        freeze_panes=None,
        storage_options=None,
        write_excel_dict=True,
        highlight_duplicates=True,
        **kwargs,
    ) -> None:
        """Write :class:`Dataset` to an Excel sheet.

        This is the analog of :meth:`pandas.DataFrame.to_excel`, so read
        the documentation for that method for descriptions of available
        parameters, notes, and examples.

        Parameters
        ----------
        write_excel_dict : bool, default True
            Whether to write a representation of the Dataset to the Excel file.
            This is needed if you intend to read the file back into a Dataset object
        highlight_duplicates : bool, default True
            Whether to highlight any duplicate rows. Only applies to Datasets with a
            ``_mp_duplicates`` column where the row value is ``True``.
        **kwargs
            All remaining keyword arguments are passed through to the underlying
            :meth:`pandas.DataFrame.to_excel` method.

        See Also
        --------
        MACPieExcelWriter : Class for writing Dataset objects into Excel sheets.
        read_excel : Read an Excel file into a macpie Dataset.
        pandas.DataFrame.to_excel : Pandas analog
        """

        from macpie.io.excel import MACPieExcelWriter

        if isinstance(excel_writer, MACPieExcelWriter):
            need_save = False
        else:
            excel_writer = MACPieExcelWriter(
                excel_writer,
                engine=engine,
                storage_options=storage_options,
            )
            need_save = True

        try:
            if isinstance(self, pd.core.dtypes.generic.ABCDataFrame):
                dset = self
            else:
                dset = self.to_frame()

            from macpie.io.formats.excel import MACPieExcelFormatter

            formatter = MACPieExcelFormatter(
                dset,
                na_rep=na_rep,
                cols=columns,
                header=header,
                float_format=float_format,
                index=index,
                index_label=index_label,
                merge_cells=merge_cells,
                inf_rep=inf_rep,
            )

            if highlight_duplicates:
                dups_col_name = get_option("column.system.duplicates")
                if dups_col_name in self.columns:
                    from macpie.io.formats.excel import highlight_axis_by_predicate

                    formatter.apply_axis_styler(
                        highlight_axis_by_predicate,
                        axis=1,
                        axis_label=dups_col_name,
                        predicate=bool,
                        color="yellow",
                    )

            if sheet_name is None:
                sheet_name = self.excel_sheetname

            formatter.write(
                excel_writer,
                sheet_name=sheet_name,
                startrow=startrow,
                startcol=startcol,
                freeze_panes=freeze_panes,
            )

            if write_excel_dict:
                to_excel_kwargs = {
                    "sheet_name": sheet_name,
                    "na_rep": na_rep,
                    "float_format": float_format,
                    "columns": columns,
                    "header": header,
                    "index": index,
                    "index_label": index_label,
                    "startrow": startrow,
                    "startcol": startcol,
                    "engine": engine,
                    "merge_cells": merge_cells,
                    "inf_rep": inf_rep,
                    "freeze_panes": freeze_panes,
                    "storage_options": storage_options,
                    "write_excel_dict": write_excel_dict,
                    "highlight_duplicates": highlight_duplicates,
                    **kwargs,
                }

                if not header:
                    header_col = None
                elif self.columns.nlevels > 1 and merge_cells:
                    # if merge_cells is False, MultiIndex header will be in
                    # legacy format, whiich is one row with dots to indicate levels.
                    header_col = list(range(0, self.columns.nlevels))
                else:
                    header_col = 0

                if not index:
                    index_col = None
                elif self.index.nlevels > 1:
                    index_col = list(range(0, self.index.nlevels))
                else:
                    index_col = 0

                # ensure successful write/read round-trip
                excel_dict = self.to_excel_dict()
                excel_dict["to_excel_kwargs"] = to_excel_kwargs
                excel_dict["read_excel_kwargs"] = {"header": header_col, "index_col": index_col}
                excel_writer.write_excel_dict(excel_dict)
        finally:
            # make sure to close opened file handles
            if need_save:
                excel_writer.close()

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "Dataset":
        """
        Construct :class:`Dataset` from a file.
        """
        from macpie.pandas.io import read_file

        df = read_file(filepath)

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

    @MethodHistory
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
        from macpie.core.combine import date_proximity

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

    @MethodHistory
    def group_by_keep_one(self, keep="all", drop_duplicates=False):
        """
        Group on the :attr:`id2_col_name` column and keep only the earliest
        or latest row in each group as determined by the date in the
        :attr:`date_col_name` column.

        Parameters
        ----------
        keep :
            See :meth:`macpie.pandas.group_by_keep_one`
        drop_duplicates :
            See :meth:`macpie.pandas.group_by_keep_one`
        """
        from macpie.core.groupby import group_by_keep_one

        return group_by_keep_one(self, keep, drop_duplicates)

    # -------------------------------------------------------------------------
    # Overriding methods
    # -------------------------------------------------------------------------

    @property
    def _constructor(self):
        """Retain Dataset as a result of an operation."""
        return Dataset

    """ In development
    @property
    def _constructor_sliced(self):
        return MacSeries
    """

    def equals(self, other: object):
        """Test whether two Datasets are equal."""
        if isinstance(other, Dataset):
            if self.name != other.name or self.tags != other.tags:
                return False
        return super().equals(other)


class LavaDataset(Dataset):
    """
    A Dataset using LAVA defaults. (LAVA is the data management system used
    at the Memory and Aging Center.) Defaults used are the following:

    * ``id_col_name`` = "InstrID"
    * ``date_col_name`` = "DCDate"
    * ``id2_col_name`` = "PIDN"
    """

    #: Default value for ``id_col_name`` of Dataset.
    FIELD_ID_COL_VALUE_DEFAULT: ClassVar[str] = "InstrID"

    #: Possible default values for ``id_col_name`` of Dataset.
    FIELD_ID_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["INSTRID", "LINK_ID"]

    #: Default value for ``id2_col_name`` of Dataset.
    FIELD_ID2_COL_VALUE_DEFAULT: ClassVar[str] = "PIDN"

    #: Possible default values for ``id2_col_name`` of Dataset.
    FIELD_ID2_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["PIDN"]

    #: Default value for ``date_col_name`` of Dataset.
    FIELD_DATE_COL_VALUE_DEFAULT: ClassVar[str] = "DCDate"

    #: Possible default values for ``date_col_name`` of Dataset.
    FIELD_DATE_COL_VALUES_POSSIBLE: ClassVar[List[str]] = ["DATE", "DCDATE", "LINK_DATE"]

    def __init__(self, *args, **kwargs):
        id_col_name = itertools.first_true(
            [kwargs.pop("id_col_name", None), LavaDataset.FIELD_ID_COL_VALUE_DEFAULT]
        )
        date_col_name = itertools.first_true(
            [kwargs.pop("date_col_name", None), LavaDataset.FIELD_DATE_COL_VALUE_DEFAULT]
        )
        id2_col_name = itertools.first_true(
            [kwargs.pop("id2_col_name", None), LavaDataset.FIELD_ID2_COL_VALUE_DEFAULT]
        )

        super().__init__(
            *args,
            id_col_name=id_col_name,
            date_col_name=date_col_name,
            id2_col_name=id2_col_name,
            **kwargs,
        )
