"""
Utilities for conversion to writer-agnostic Excel representation.
"""

from typing import Iterable

from pandas import MultiIndex

from pandas.io.formats.excel import ExcelCell, ExcelFormatter
from pandas.io.formats.format import get_level_lengths
from pandas.io.formats.printing import pprint_thing


class MACPieExcelFormatter(ExcelFormatter):
    def _format_header_mi(self) -> Iterable[ExcelCell]:
        if not (self._has_aliases or self.header):
            return

        columns = self.columns
        level_strs = columns.format(sparsify=self.merge_cells, adjoin=False, names=False)
        level_lengths = get_level_lengths(level_strs)
        coloffset = 0
        lnum = 0

        if self.columns.nlevels > 1 and not self.index:
            # kludgey fix for: https://github.com/pandas-dev/pandas/issues/27772
            # All other code in this method should be same as parent
            coloffset -= 1

        if self.index and isinstance(self.df.index, MultiIndex):
            coloffset = len(self.df.index[0]) - 1

        if self.merge_cells:
            # Format multi-index as a merged cells.
            for lnum, name in enumerate(columns.names):
                yield ExcelCell(
                    row=lnum,
                    col=coloffset,
                    val=name,
                    style=self.header_style,
                )

            for lnum, (spans, levels, level_codes) in enumerate(
                zip(level_lengths, columns.levels, columns.codes)
            ):
                values = levels.take(level_codes)
                for i, span_val in spans.items():
                    spans_multiple_cells = span_val > 1
                    yield ExcelCell(
                        row=lnum,
                        col=coloffset + i + 1,
                        val=values[i],
                        style=self.header_style,
                        mergestart=lnum if spans_multiple_cells else None,
                        mergeend=(coloffset + i + span_val if spans_multiple_cells else None),
                    )
        else:
            # Format in legacy format with dots to indicate levels.
            for i, values in enumerate(zip(*level_strs)):
                v = ".".join(map(pprint_thing, values))
                yield ExcelCell(lnum, coloffset + i + 1, v, self.header_style)

        self.rowcounter = lnum

    def _format_regular_rows(self) -> Iterable[ExcelCell]:
        # kludgey fix for: https://github.com/pandas-dev/pandas/issues/27772
        if self.columns.nlevels > 1 and self.index:
            self.rowcounter -= 1

        yield from super()._format_regular_rows()

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
