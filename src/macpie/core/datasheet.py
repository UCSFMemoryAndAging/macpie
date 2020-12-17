import re

from macpie import util


SHEETNAME_CHARS_LIMIT = 31


class Datasheet:

    def __init__(self,
                 name,
                 df=None,
                 display_name=None,
                 display_header=True,
                 display_index=False,
                 index_label=None,
                 startrow=0,
                 startcol=0):
        self.name = name
        self.df = df
        self.display_name = name if display_name is None else display_name
        self.display_header = display_header
        self.display_index = display_index
        self.index_label = index_label
        self.startrow = startrow
        self.startcol = startcol
        self.num_header_rows = self.df.columns.nlevels
        self.num_index_cols = self.df.index.nlevels

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'name={self.name!r}, '
            f'display_name={self.display_name!r})'
        )

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        if value is None:
            raise ValueError("'display_name' cannot be None")
        value = value[:SHEETNAME_CHARS_LIMIT]  # Truncate if too long
        value = value.strip()  # Strip leading and trailing spaces.
        value = re.sub(' +', ' ', value)  # Spaces to single space.
        value = re.sub(r'[ ]', '_', value)  # Hyphens and spaces to underscore.
        value = re.sub('[^0-9a-zA-Z_()-]', '', value)  # Remove invalid characters.

        self._display_name = value

    def add_suffix(self, suffix):
        self.name = util.string.add_suffix(self.name, suffix)
        self.display_name = util.string.add_suffix(self.display_name, suffix, SHEETNAME_CHARS_LIMIT)

    def to_dict(self):
        return {
            'sheetname': self.display_name,
            'display_header': self.display_header,
            'display_index': self.display_index,
            'index_label': self.index_label,
            'startrow': self.startrow,
            'startcol': self.startcol,
            'num_header_rows': self.num_header_rows,
            'num_index_cols': self.num_index_cols,
            'df_rows': self.df.mac.num_rows(),
            'df_cols': self.df.mac.num_cols()
        }

    def to_excel(self, excel_writer):
        self.df.to_excel(
            excel_writer=excel_writer,
            sheet_name=self.display_name,
            header=self.display_header,
            index=self.display_index,
            index_label=self.index_label,
            startrow=self.startrow,
            startcol=self.startcol
        )