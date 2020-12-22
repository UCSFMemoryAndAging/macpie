import re

from macpie import util


SHEETNAME_CHARS_LIMIT = 31


class Datasheet:
    """
    Encapsulate a "sheet" of data similar to an Excel worksheet.
    Parameters align with :meth:`pandas.DataFrame.to_excel()` method, allowing
    for easy writes to an Excel file.
    """

    def __init__(self,
                 name,
                 df=None,
                 display_name=None,
                 display_header=True,
                 display_index=False,
                 index_label=None,
                 startrow=0,
                 startcol=0):
        #: Name of this Datasheet
        self.name = name

        #: A pandas DataFrame representing the data of this Datasheet
        self.df = df

        self.display_name = name if display_name is None else display_name
        """
        Name to display in any output, with formatting logic applied:
            * Truncate to 31 chars (Excel worksheet name limit)
            * Strip leading and trailing spaces.
            * Spaces to single space.
            * Hyphens and spaces to underscore.
            * Remove invalid characters (only ``[^0-9a-zA-Z_()-]`` allowed).
        """

        #: Whether to write out the column names. If a list of string is given
        #: it is assumed to be aliases for the column names.
        self.display_header = display_header

        #: Whether to write row names (index).
        self.display_index = display_index

        #: Column label for index column(s) if desired. If not specified, and
        #: display_header and display_index are True, then the index names are used.
        #: A sequence should be given if the DataFrame uses MultiIndex.
        self.index_label = index_label

        #: Upper left cell row to dump DataFrame.
        self.startrow = startrow

        #: Upper left cell column to dump DataFrame.
        self.startcol = startcol

        #: Number of top-most rows used for the column headers
        self.num_header_rows = self.df.columns.nlevels

        #: Number of left-most columns used for the row indexes
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
        """
        Add a suffix to the ``name`` and ``display_name`` fields
        """
        self.name = util.string.add_suffix(self.name, suffix)
        self.display_name = util.string.add_suffix(self.display_name, suffix, SHEETNAME_CHARS_LIMIT)

    def to_dict(self):
        """
        Convert the Datasheet to a dictionary.
        """
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
        """
        Write to an Excel file.

        :param excel_writer: str representing a filepath,
                             or :class:`pandas.ExcelWriter` object
        """
        self.df.to_excel(
            excel_writer=excel_writer,
            sheet_name=self.display_name,
            header=self.display_header,
            index=self.display_index,
            index_label=self.index_label,
            startrow=self.startrow,
            startcol=self.startcol
        )
