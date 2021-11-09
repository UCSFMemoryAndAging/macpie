import xlsxwriter


def tlset_sheet(tlset, ws, format_bold, format_text_wrap, freeze_panes=True):
    """Completes given worksheet from given Dataset."""

    _package = tlset._package(dicts=False)

    for i, sep in enumerate(tlset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))

    for i, row in enumerate(_package):
        row_number = i + 1
        for j, col in enumerate(row):
            ws.write(i, j, col)

            # bold headers
            if (row_number == 1) and tlset.headers:
                ws.write(i, j, col, format_bold)
                if freeze_panes:
                    # Freeze only after first line
                    ws.freeze_panes("A2")

            # bold separators
            elif len(row) < tlset.width:
                ws.write(i, j, col, format_bold)

            # wrap the rest
            else:
                try:
                    str_col_value = str(col)
                except TypeError:
                    str_col_value = ""

                if "\n" in str_col_value:
                    ws.write(i, j, col, format_text_wrap)
                else:
                    ws.write(i, j, col)


class XlsxWriterAutofitColumnsWorksheet(xlsxwriter.worksheet.Worksheet):
    """Simulates AutoFit columns in Excel."""

    def __init__(self):
        super().__init__()

        # Store column widths
        self.max_column_widths = {}

    def set_autofit_column_width(self):
        for column, width in self.max_column_widths.items():
            self.set_column(column, column, width)

    def _write_string(self, row, col, string, cell_format=None):
        # Overridden method to store the maximum string width
        # seen in each column.

        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Set the min width for the cell. In some cases this might be the
        # default width of 8.43. In this case we use 0 and adjust for all
        # string widths.
        min_width = 0

        # Check if it the string is the largest we have seen for this column.
        string_width = XlsxWriterAutofitColumnsWorksheet.excel_string_width(string)
        if string_width > min_width:
            max_width = self.max_column_widths.get(col, min_width)
            if string_width > max_width:
                self.max_column_widths[col] = string_width

        return super()._write_string(row, col, string, cell_format)

    @staticmethod
    def excel_string_width(str):
        """Calculate the length of the string in Excel character units."""

        string_width = len(str)

        if string_width == 0:
            return 0
        else:
            return string_width * 1.1
