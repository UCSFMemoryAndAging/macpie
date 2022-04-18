"""
Utilities for conversion to writer-agnostic Excel representation.
"""

from typing import Callable, Iterable

import numpy as np
import pandas as pd
import pandas.core.common as com
from pandas import Index, MultiIndex
from pandas.io.formats.excel import CSSToExcelConverter, ExcelCell, ExcelFormatter
from pandas.io.formats.format import get_level_lengths
from pandas.io.formats.printing import pprint_thing


def highlight_axis_by_predicate(s: pd.Series, axis_label=None, predicate=None, color="yellow"):
    if predicate is None:
        predicate = bool

    style_converter = CSSToExcelConverter()
    css = f"background-color: {color}"
    xlstyle = style_converter(css)

    if predicate(s[axis_label]):
        return xlstyle
    return None


class MACPieExcelFormatter(ExcelFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def axis_styler(self):
        if "_axis_styler" in self.__dict__:
            return self._axis_styler
        return None

    def apply_axis_styler(self, func: Callable, axis=0, **kwargs):
        # styles an entire axis
        # see highlight_row_by_column_predicate for an example
        self._axis_styler = (axis, func, kwargs)

    def _format_header_mi(self) -> Iterable[ExcelCell]:
        """Currently, as of pandas 1.3.4, still cannot write to Excel
        with MultiIndex columns and no index ('index'=False).
        Added a few hacks to make it work until hopefully it gets
        implemented soon.
        TODO: Implement a better solution.
        """
        if not (self._has_aliases or self.header):
            return

        columns = self.columns
        level_strs = columns.format(sparsify=self.merge_cells, adjoin=False, names=False)
        level_lengths = get_level_lengths(level_strs)
        coloffset = 0
        lnum = 0

        if self.index and isinstance(self.df.index, MultiIndex):
            coloffset = len(self.df.index[0]) - 1

        if not self.index:
            # hack 1/2
            coloffset = coloffset - 1

        if self.merge_cells:
            # Format multi-index as a merged cells.
            if self.index:
                # hack 2/2
                # if not self.index, skip this to avoid negative col index
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

    def _format_hierarchical_rows(self) -> Iterable[ExcelCell]:
        """Kludgey fix for: https://github.com/pandas-dev/pandas/issues/27772
        Code is verbatim from parent EXCEPT for the 'pass' line and the following
        commented out line
        """
        if self._has_aliases or self.header:
            self.rowcounter += 1

        gcolidx = 0

        if self.index:
            index_labels = self.df.index.names
            # check for aliases
            if self.index_label and isinstance(self.index_label, (list, tuple, np.ndarray, Index)):
                index_labels = self.index_label

            # MultiIndex columns require an extra row
            # with index names (blank if None) for
            # unambiguous round-trip, unless not merging,
            # in which case the names all go on one row Issue #11328
            if isinstance(self.columns, MultiIndex) and self.merge_cells:
                pass
                # self.rowcounter += 1

            # if index labels are not empty go ahead and dump
            if com.any_not_none(*index_labels) and self.header is not False:

                for cidx, name in enumerate(index_labels):
                    yield ExcelCell(self.rowcounter - 1, cidx, name, self.header_style)

            if self.merge_cells:
                # Format hierarchical rows as merged cells.
                level_strs = self.df.index.format(sparsify=True, adjoin=False, names=False)
                level_lengths = get_level_lengths(level_strs)

                for spans, levels, level_codes in zip(
                    level_lengths, self.df.index.levels, self.df.index.codes
                ):

                    values = levels.take(
                        level_codes,
                        allow_fill=levels._can_hold_na,
                        fill_value=levels._na_value,
                    )

                    for i, span_val in spans.items():
                        spans_multiple_cells = span_val > 1
                        yield ExcelCell(
                            row=self.rowcounter + i,
                            col=gcolidx,
                            val=values[i],
                            style=self.header_style,
                            mergestart=(
                                self.rowcounter + i + span_val - 1
                                if spans_multiple_cells
                                else None
                            ),
                            mergeend=gcolidx if spans_multiple_cells else None,
                        )
                    gcolidx += 1

            else:
                # Format hierarchical rows with non-merged values.
                for indexcolvals in zip(*self.df.index):
                    for idx, indexcolval in enumerate(indexcolvals):
                        yield ExcelCell(
                            row=self.rowcounter + idx,
                            col=gcolidx,
                            val=indexcolval,
                            style=self.header_style,
                        )
                    gcolidx += 1

        yield from self._generate_body(gcolidx)

    def _generate_body(self, coloffset: int) -> Iterable[ExcelCell]:
        if self.axis_styler:
            axis, func, kwargs = self.axis_styler
            if axis == 1:
                # Write the body of the frame data row by row
                for rowidx in range(len(self.df.index)):
                    series = self.df.iloc[rowidx]
                    xlstyle = func(series, **kwargs)
                    for i, val in enumerate(series):
                        yield ExcelCell(
                            row=self.rowcounter + rowidx, col=i + coloffset, val=val, style=xlstyle
                        )
            elif axis == 0:
                # Write the body of the frame data column by column
                for colidx in range(len(self.columns)):
                    series = self.df.iloc[:, colidx]
                    xlstyle = func(series, **kwargs)
                    for i, val in enumerate(series):
                        yield ExcelCell(
                            row=self.rowcounter + i, col=colidx + coloffset, val=val, style=xlstyle
                        )
        else:
            yield from super()._generate_body(coloffset)

    def _generate_body_rowwise(self, coloffset: int) -> Iterable[ExcelCell]:
        # useful if you want to generate the body row-wise, instead of
        # the default, which is column-wise
        if self.styler is None:
            styles = None
        else:
            styles = self.styler._compute().ctx
            if not styles:
                styles = None
        xlstyle = None

        for rowidx in range(len(self.df.index)):
            series = self.df.iloc[rowidx]
            for i, val in enumerate(series):
                if styles is not None:
                    css = ";".join([a + ":" + str(v) for (a, v) in styles[rowidx, i]])
                    xlstyle = self.style_converter(css)
                yield ExcelCell(self.rowcounter + rowidx, i + coloffset, val, xlstyle)

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
