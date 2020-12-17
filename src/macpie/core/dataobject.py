import json
from pathlib import Path
from typing import ClassVar, List

import numpy as np
import pandas as pd

from macpie import errors, io


class DataObject:

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        id_col: str = None,
        date_col: str = None,
        id2_col: str = None,
        filepath: Path = None,
        display_name: str = None
    ):
        self.name = name
        self.df = self._df_orig = df
        self.id_col = id_col
        self.date_col = date_col
        self.id2_col = id2_col
        self.filepath = filepath
        self.display_name = name if display_name is None else display_name

        if self.date_col is not None:
            self.date_col = self.df.mac.to_datetime(self.date_col)

        if self.id2_col is not None:
            try:
                self.id2_col = self.df.mac.get_col_name(self.id2_col)
            except KeyError:
                raise errors.DataObjectID2ColKeyError(
                    f"ID2 column '{self.id2_col}' in dataobject '{self.name}'' not found"
                )

        if self.id_col is not None:
            try:
                self.id_col = self.df.mac.get_col_name(self.id_col)
            except KeyError:
                raise errors.DataObjectIDColKeyError(
                    f"ID column '{self.id_col}' in dataobject '{self.name}'' not found"
                )

            if self.df[self.id_col].isnull().any():
                raise errors.DataObjectIDColKeyError(
                    f"ID column '{self.id_col}' in dataobject '{self.name}'' has null values,"
                    " which are not allowed"
                )

            if self.df[self.id_col].duplicated().any():
                raise errors.DataObjectIDColDuplicateKeyError(
                    f"ID column '{self.id_col}' in dataobject '{self.name}'' has duplicates,"
                    " which are not allowed"
                )

        if self.id_col is None:
            self.id_col = 'mp_id_col'
            sort_cols = []
            if self.id2_col is not None:
                sort_cols.append(self.id2_col)
            if self.date_col is not None:
                sort_cols.append(self.date_col)

            self.df = self.df.sort_values(by=sort_cols)
            self.df.insert(0, self.id_col, np.arange(1, len(self.df) + 1))

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        if value is None:
            raise ValueError("'df' cannot be None")
        self._df = value

    @property
    def df_orig(self):
        return self._df_orig

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'name={self.name!r}, '
            f'id_col={self.id_col!r}, '
            f'date_col={self.date_col!r}, '
            f'id2_col={self.id2_col!r})'
        )

    def rename_id_col(self, new_id_col):
        old_id_col = self.id_col
        self.id_col = new_id_col
        if old_id_col is not None and old_id_col in self._df.columns:
            self.df = self.df.rename(columns={old_id_col: new_id_col})

    def to_dict(self):
        return {
            'name': self.name,
            'id_col': self.id_col,
            'date_col': self.date_col,
            'id2_col': self.id2_col,
            'filepath': str(self.filepath.resolve()),
            'display_name': self.display_name,
            'rows': self.df.mac.num_rows(),
            'cols': self.df.mac.num_cols()
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_file(cls,
                  filepath,
                  name,
                  id_col=None,
                  date_col=None,
                  id2_col=None,
                  display_name=None) -> "DataObject":

        df = io.file_to_dataframe(filepath)

        return cls(name,
                   id_col=id_col,
                   date_col=date_col,
                   id2_col=id2_col,
                   df=df,
                   filepath=filepath,
                   display_name=display_name)


class LavaDataObject(DataObject):

    FIELD_ID_COL_VALUE_DEFAULT : ClassVar[str] = 'instrid'
    FIELD_ID2_COL_VALUE_DEFAULT : ClassVar[str] = 'pidn'
    FIELD_ID_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['ID', 'PIDN', 'VID', 'INSTRID', 'SPECID']
    FIELD_DATE_COL_VALUE_DEFAULT : ClassVar[str] = 'dcdate'
    FIELD_DATE_COL_VALUES_POSSIBLE : ClassVar[List[str]] = ['DATE', 'DCDATE']

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        id_col: str = None,
        date_col: str = None,
        id2_col: str = None,
        filepath: Path = None,
        display_name: str = None
    ):
        super().__init__(
            name,
            df,
            id_col,
            date_col if date_col is not None else LavaDataObject.FIELD_DATE_COL_VALUE_DEFAULT,
            id2_col if id2_col is not None else LavaDataObject.FIELD_ID2_COL_VALUE_DEFAULT,
            filepath,
            display_name
        )