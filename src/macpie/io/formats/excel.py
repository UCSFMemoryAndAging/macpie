"""
Utilities for conversion to writer-agnostic Excel representation.
"""

import pandas as pd


class MACPieExcelFormatter(pd.io.formats.excel.ExcelFormatter):
    def write(self, writer, sheet_name=None, startrow=0, startcol=0, freeze_panes=None):
        num_rows, num_cols = self.df.shape
        if num_rows > self.max_rows or num_cols > self.max_cols:
            raise ValueError(
                f"This sheet is too large! Your sheet size is: {num_rows}, {num_cols} "
                f"Max sheet size is: {self.max_rows}, {self.max_cols}"
            )

        formatted_cells = self.get_formatted_cells()

        writer.write_cells(
            formatted_cells,
            sheet_name,
            startrow=startrow,
            startcol=startcol,
            freeze_panes=freeze_panes,
        )
