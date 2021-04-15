from typing import ClassVar, List, Optional

import numpy as np
import pandas as pd
import tablib as tl

from macpie._config import get_option
from macpie.exceptions import (
    DatasetIDColError,
    DatasetDateColError,
    DatasetID2ColError
)
from macpie.io.excel import MACPieExcelFormatter
from macpie.pandas.general import get_col_name, to_datetime
from macpie.tools import sequence as seqtools
from macpie.tools import string as strtools
from macpie.util.decorators import TrackHistory


class Dataset:
    """
    Two-dimensional tabular data with key fields commonly used in
    clinical research data: form ID, date of collection, and subject id.
    The core MACPie data structure.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        id_col: str = None,
        date_col: str = None,
        id2_col: str = None,
        name: str = None,
        tags: List[str] = []
    ):
        #: The column in the :class:`pandas.DataFrame` representing the primary key/index
        #: of the Dataset. Typically used for unique IDs of a clinical
        #: research subject's data record (e.g. form, assessment, assay)
        self._id_col = id_col

        #: The column in the :class:`pandas.DataFrame` representing the primary date column
        #: of the Dataset. Typically used for the date the data was collected.
        self._date_col = date_col

        #: The column in the :class:`pandas.DataFrame` representing the secondary key/index
        #: of the Dataset. Typically used for the ID of the subject themselves.
        self._id2_col = id2_col

        #: The name of this Dataset.
        self.name = name

        #: Arbitrary tags for the Dataset that can be filtered on later.
        self.tags = tags

        #: The :class:`pandas.DataFrame` representing the actual data.
        self.df = self._df_orig = df

        self._misc_init()

    def __len__(self):
        return self.height

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'name={self.name!r}, '
            f'id_col={self._id_col!r}, '
            f'date_col={self._date_col!r}, '
            f'id2_col={self._id2_col!r}, '
            f'tags={self.tags!r})'
        )

    # -------------------------------------------------------------------------
    # Internals
    # -------------------------------------------------------------------------

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

    def _misc_init(self):
        # used to sort tags if needed, especially for generating display_name
        self._tag_order = [
            get_option("dataset.tag.anchor"),
            get_option("dataset.tag.secondary"),
            get_option("dataset.tag.mergeable"),
            get_option("dataset.tag.linked"),
            get_option("dataset.tag.duplicates")
        ]

    # -------------------------------------------------------------------------
    # Read-Only Properties
    # -------------------------------------------------------------------------

    @property
    def df_orig(self):
        return self._df_orig

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
    def key_cols(self):
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
        sys_col_prefix = get_option("column.system.prefix")
        return [col for col in self.df.columns if col.startswith(sys_col_prefix)]

    @property
    def non_key_cols(self):
        key_and_sys_cols = self.key_cols + self.sys_cols
        return [col for col in self.df.columns if col not in key_and_sys_cols]

    @property
    def all_fields(self):
        return [(self.name, col) for col in self.df.columns]

    @property
    def key_fields(self):
        return [(self.name, col) for col in self.key_cols]

    @property
    def sys_fields(self):
        return [(self.name, col) for col in self.sys_cols]

    @property
    def non_key_fields(self):
        return [(self.name, col) for col in self.non_key_cols]

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
        if '_history' in self.__dict__:
            return self.__dict__['_history']
        return []

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

    def copy_from_dset(self, dset, suffix=None):
        """
        `dset` is usually the parent Dataset that this one derived from,
        so joining on the key columns

        Typical case is `dset` is a primary, and this one is a secondary, and we need
        to copy over the values from primary into this one.
        """
        # cannot use get_option for default value of keyword params,
        # so setting it here
        if suffix is None:
            suffix = get_option("operators.binary.column_suffixes")[0]

        left_on = []
        right_on = []

        for col in self._df.columns:
            if dset.id_col and col == (dset.id_col + suffix):
                left_on.append(dset.id_col)
                right_on.append(col)
            if dset.date_col and col == (dset.date_col + suffix):
                left_on.append(dset.date_col)
                right_on.append(col)
            if dset.id2_col and col == (dset.id2_col + suffix):
                left_on.append(dset.id2_col)
                right_on.append(col)

        if not left_on or not right_on:
            raise KeyError("No columns to merge on")

        left_df = dset.df[left_on].copy()
        left_df.columns = left_df.columns.map(lambda x: str(x) + '_temp')
        left_on = [col + "_temp" for col in left_on]

        result = pd.merge(
            left_df,
            self.df,
            how='left',
            left_on=left_on,
            right_on=right_on,
            suffixes=('_temp', None)
        )

        result = result.drop(columns=right_on)

        result = result.mac.replace_suffix('_temp', suffix)

        self._df = result

    # -------------------------------------------------------------------------
    # Tag Methods
    # -------------------------------------------------------------------------

    def add_tag(self, tag):
        self._tags.append(tag)

    def clear_tags(self):
        self._tags = []

    def replace_tag(self, old_tag, new_tag):
        if set(old_tag).issubset(set(self._tags)):
            old_tag = seqtools.maybe_make_list(old_tag)
            new_tag = seqtools.maybe_make_list(new_tag)
            for ot in old_tag:
                self._tags.remove(ot)
            self._tags.extend(new_tag)

    def has_tag(self, tag):
        """Returns true if Dataset contains tag."""

        if tag is None:
            return False
        elif isinstance(tag, str):
            return (tag in self._tags)
        else:
            return bool(len(set(tag) & set(self._tags)))

    # -------------------------------------------------------------------------
    # Dataset Display Name Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def create_display_name(name, tags=[], tag_order=[], max_length: int = -1):
        if not tags:
            return name[:max_length] if max_length > -1 else name

        display_name = name
        if tag_order:
            tags.sort(key=lambda i: tag_order.index(i) if i in tag_order else -1)

        for tag in tags:
            display_name = strtools.add_suffix(display_name, "_" + tag, max_length)

        return display_name

    def get_display_name(self, tags=[], max_length: int = -1):
        return Dataset.create_display_name(self.name, self.tags, self._tag_order, max_length)

    # -------------------------------------------------------------------------
    # Dataset Columns Methods
    # -------------------------------------------------------------------------

    def create_id_col(self, col_name='mp_id_col', start_index=1):
        if self._id_col is not None:
            raise ValueError(f'"id_col" with value "{self._id_col}"" already exists')

        # self.sort_by_id2()
        # create an id_col called 'mp_id_col' with index starting from 1
        self._id_col = col_name
        self._df.insert(0, col_name, np.arange(start_index, len(self._df) + 1))

    def drop_col(self, col):
        self._df = self._df.drop(columns=col)

    def keep_fields(self, selected_fields):
        if self.name in selected_fields.to_dict():
            self.keep_cols(selected_fields.to_dict()[self.name])

    def keep_cols(self, cols):
        cols_to_keep = self.key_cols

        # preserve order of the key columns by sorting them according
        # to existing order
        cols_to_keep.sort(key=lambda i: self._df.columns.tolist().index(i))

        cols = seqtools.maybe_make_list(cols)
        cols_to_keep.extend([c for c in cols if c not in cols_to_keep])
        self._df = self._df[cols_to_keep]

    def rename_id_col(self, new_id_col):
        """
        Reset the ``id_col`` field to ``new_id_col``
        """
        old_id_col = self._id_col
        self._id_col = new_id_col
        if old_id_col is not None and old_id_col in self._df.columns:
            self._df = self._df.rename(columns={old_id_col: new_id_col})

    def rename_col(self, old_col, new_col):
        """
        Reset the ``id_col`` field to ``new_id_col``
        """
        if old_col in self.non_key_cols or old_col in self.sys_cols:
            self._df = self._df.rename(columns={old_col: new_col})
        else:
            raise KeyError(f"Column '{old_col}' not in dataset or is a key column.")

    # -------------------------------------------------------------------------
    # Sorting
    # -------------------------------------------------------------------------

    def sort_by_id2(self):
        sort_cols = []
        if self._id2_col:
            sort_cols.append(self._id2_col)
        if self._date_col:
            sort_cols.append(self._date_col)
        if self._id_col:
            sort_cols.append(self._id_col)
        if sort_cols:
            self._df = self._df.sort_values(by=sort_cols, na_position='last')

    # -------------------------------------------------------------------------
    # I/O Methods
    # -------------------------------------------------------------------------

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "Dataset":
        """
        Construct Dataset from a file.
        """
        from macpie.pandas.io import file_to_dataframe
        df = file_to_dataframe(filepath)

        return cls(df,
                   id_col=kwargs.get('id_col'),
                   date_col=kwargs.get('date_col'),
                   id2_col=kwargs.get('id2_col'),
                   name=kwargs.get('name', filepath.stem),
                   tags=kwargs.get('tags'))

    @classmethod
    def from_excel_sheet(cls, filepath, dict_repr, id_dropna=False):
        dset_sheet_name = Dataset.create_display_name(dict_repr['name'], dict_repr['tags'], max_length=31)
        dset_df = pd.read_excel(filepath, sheet_name=dset_sheet_name, index_col=None, header=0)

        if id_dropna:
            dset_df = dset_df.dropna(subset=[dict_repr['id_col']])

        return cls(dset_df,
                   id_col=dict_repr['id_col'],
                   date_col=dict_repr['date_col'],
                   id2_col=dict_repr['id2_col'],
                   name=dict_repr['name'],
                   tags=dict_repr['tags'])

    def to_dict(self):
        """
        Convert the Dataset to a dictionary.
        """
        return {
            'name': self.name,
            'id_col': self._id_col,
            'date_col': self._date_col,
            'id2_col': self._id2_col,
            'tags': self.tags,
            'rows': self.height,
            'cols': self.width
        }

    def to_tablib(self):
        tlset = tl.Dataset()
        tlset.title = self.get_display_name()
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
        formatter = MACPieExcelFormatter(
            self,
            na_rep=na_rep,
            cols=columns,
            header=header,
            float_format=float_format,
            index=index,
            index_label=index_label,
            merge_cells=merge_cells,
            inf_rep=inf_rep
        )
        formatter.write(
            excel_writer,
            sheet_name=sheet_name,
            startrow=startrow,
            startcol=startcol,
            freeze_panes=freeze_panes,
            engine=engine,
            storage_options=storage_options
        )

    # -------------------------------------------------------------------------
    # Data Transformation Methods
    # -------------------------------------------------------------------------

    @TrackHistory
    def date_proximity(
        self,
        anchor_dset: "Dataset",
        get: str = 'all',
        when: str = 'earlier_or_later',
        days: int = 90,
        dropna: bool = False,
        drop_duplicates: bool = False,
        duplicates_indicator: bool = False,
        merge_suffixes=get_option("operators.binary.column_suffixes")
    ) -> None:
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
            merge_suffixes=merge_suffixes
        )

    @TrackHistory
    def group_by_keep_one(self, keep="all", drop_duplicates=False):
        from macpie.core.reshape.group_by_keep_one import group_by_keep_one
        return group_by_keep_one(self, keep, drop_duplicates)


class LavaDataset(Dataset):

    FIELD_ID_COL_VALUE_DEFAULT : ClassVar[str] = 'InstrID'
    FIELD_ID_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['INSTRID', 'LINK_ID']
    FIELD_ID2_COL_VALUE_DEFAULT : ClassVar[str] = 'PIDN'
    FIELD_ID2_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['PIDN']
    FIELD_DATE_COL_VALUE_DEFAULT : ClassVar[str] = 'DCDate'
    FIELD_DATE_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['DATE', 'DCDATE', 'LINK_DATE']

    def __init__(
        self,
        df: pd.DataFrame,
        **kwargs
    ):
        super().__init__(
            df,
            id_col=kwargs.get('id_col', LavaDataset.FIELD_ID_COL_VALUE_DEFAULT),
            date_col=kwargs.get('date_col', LavaDataset.FIELD_DATE_COL_VALUE_DEFAULT),
            id2_col=kwargs.get('id2_col', LavaDataset.FIELD_ID2_COL_VALUE_DEFAULT),
            name=kwargs.get('name'),
            tags=kwargs.get('tags')
        )

    @classmethod
    def from_file(cls, filepath, **kwargs) -> "Dataset":
        """
        Construct LavaDataset from a file.
        """
        from macpie.pandas.io import file_to_dataframe
        df = file_to_dataframe(filepath)
        name = kwargs.pop('name', filepath.stem)
        return cls(df, name=name, **kwargs)
