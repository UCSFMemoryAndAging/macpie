from pathlib import Path, PurePath
from typing import ClassVar

import openpyxl as pyxl
import pandas as pd

from .datasheet import Datasheet


class Databook:

    SHEETNAME_SHEETS : ClassVar[str] = '_sheets'

    def __init__(self):
        self._sheets = []

    def __getitem__(self, index):
        if isinstance(index, int):
            return self._sheets[index]
        else:
            raise ValueError("%s is not a valid index." % index)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'sheets={self._sheets!r})'
        )

    def add_sheet(self, datasheet: Datasheet):
        for d in self._sheets:
            if d.name == datasheet.name:
                raise ValueError(f"Datasheet '{d.name}' already exists")

        self._sheets.append(datasheet)

    def add_metadata_sheet(self, datasheet: Datasheet):
        datasheet.df = datasheet.df.mac.json_dumps_contents()
        self._sheets.append(datasheet)

    def read_metadata_sheet(self, filepath, sheetname, index=None):
        sheet_data = pd.read_excel(filepath, sheet_name=sheetname, engine='openpyxl')
        sheet_data = sheet_data.mac.json_loads_contents()
        if index is not None:
            sheet_data = sheet_data.set_index(index)
        return sheet_data.to_dict('index')

    def to_excel(self, filepath: Path = None, mode='w'):
        filepath = self._validate_filepath(filepath)
        writer = pd.ExcelWriter(str(filepath), engine='openpyxl', mode=mode)

        sheet_metadata = []
        for ds in self._sheets:
            sheet_metadata.append(ds.metadata_list())
            ds.to_excel(writer)

        sheet_metadata_df = pd.DataFrame(data=sheet_metadata, columns=Datasheet.metadata_col_headers).mac.json_dumps_contents()
        Datasheet(self.SHEETNAME_SHEETS, sheet_metadata_df, display_index=False).to_excel(writer)

        writer.save()
        self.format_excel(filepath)

    def format_excel(self, filepath):
        wb = pyxl.load_workbook(filepath)
        sheet_metadata_dict = self.read_metadata_sheet(filepath, self.SHEETNAME_SHEETS, index='worksheet')
        for sheetname, sheetprops in sheet_metadata_dict.items():
            ws = wb[sheetname]
            if not sheetname.startswith('_'):
                if sheetprops['display_header'] is True:
                    # create excel auto filters if there is a header
                    if sheetprops['display_index'] is False:
                        filter_range = ('A'
                                        + str(sheetprops['num_header_rows'])
                                        + ":"
                                        + pyxl.utils.get_column_letter(ws.max_column)
                                        + str(ws.max_row))
                    elif sheetprops['display_index'] is True:
                        filter_range = (pyxl.utils.get_column_letter(sheetprops['num_index_cols'] + 1)
                                        + str(sheetprops['num_header_rows'])
                                        + ":"
                                        + pyxl.utils.get_column_letter(ws.max_column)
                                        + str(ws.max_row))
                        if sheetprops['num_header_rows'] > 1 and sheetprops['num_index_cols'] <= 1:
                            # special case to handle pandas and openpyxl bugs when writing dataframes with multiindex
                            # https://stackoverflow.com/questions/54682506/openpyxl-in-python-delete-rows-function-breaks-the-merged-cell
                            # https://github.com/pandas-dev/pandas/issues/27772
                            # another openpyxl bug where if num_index_cols > 1, deleting rows doesn't work if adjacent
                            # cells in the index have been merged
                            row_to_delete = sheetprops['num_header_rows'] + 1
                            ws.delete_rows(row_to_delete)
                    ws.auto_filter.ref = filter_range
        wb.save(filepath)

    def _validate_filepath(self, filepath):
        if filepath is None:
            raise ValueError("'filepath' cannot be None")
        if isinstance(filepath, PurePath):
            filepath = filepath.resolve()
        elif isinstance(filepath, str):
            filepath = Path(filepath).resolve()
        else:
            raise ValueError(
                f'For argument "filepath" expected type path or string, received '
                f"type {type(filepath).__name__}."
            )
        return filepath
