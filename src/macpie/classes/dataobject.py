from pathlib import Path

import numpy as np
import pandas as pd

from macpie.exceptions import DataObjectIDColKeyError, DataObjectID2ColKeyError
from macpie.io import file_to_dataframe


class DataObject:

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        id_col: str = None,
        date_col: str = None,
        id2_col: str = None,
        filepath: Path = None
    ):
        self.name = name
        self.df = self._df_orig = df
        self.id_col = id_col
        self.date_col = date_col
        self.id2_col = id2_col
        self.filepath = filepath

        if self.date_col is not None:
            self.date_col = self.df.mac.to_datetime(self.date_col)

        if self.id2_col is not None:
            try:
                self.id2_col = self.df.mac.get_col_name(self.id2_col)
            except KeyError:
                raise DataObjectID2ColKeyError(f"ID2 column '{self.id2_col}' in dataobject '{self.name}'' not found")

        if self.id_col is not None:
            try:
                self.id_col = self.df.mac.get_col_name(self.id_col)
            except KeyError:
                raise DataObjectIDColKeyError(f"ID column '{self.id_col}' in dataobject '{self.name}'' not found")

            if self.df[self.id_col].duplicated().any():
                raise DataObjectIDColKeyError(
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
            'rows': self.df.mac.num_rows(),
            'cols': self.df.mac.num_cols()
        }

    @classmethod
    def from_file(cls, filepath, name, id_col=None, date_col=None, id2_col=None) -> "DataObject":
        df = file_to_dataframe(filepath)
        return cls(name, id_col=id_col, date_col=date_col, id2_col=id2_col, df=df, filepath=filepath)
