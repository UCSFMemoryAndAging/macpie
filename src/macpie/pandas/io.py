"""
Module contains tools for processing files (e.g. csv, xlsx) into pandas objects
"""

import openpyxl as pyxl
import pandas as pd
import tablib as tl

from macpie.exceptions import ParserError
from macpie.tools import io as iotools
from macpie.tools import openpyxl as openpyxltools


def file_to_dataframe(filepath):
    """Parse a file into a :class:`pandas.DataFrame`.

    :param filepath: File path
    :raises ParserError:
    :return: a :class:`pandas.DataFrame` object
    """
    if iotools.has_csv_extension(filepath):
        return csv_to_dataframe(filepath, engine='pandas')
    if iotools.has_excel_extension(filepath):
        return excel_to_dataframe(filepath, engine='openpyxl')
    raise ParserError(f'Error parsing file due to invalid file extension: {filepath}')


def csv_to_dataframe(filepath_or_buffer, engine='pandas'):
    """Parse a csv file into a :class:`pandas.DataFrame`.

    :param filepath: File path
    :param engine: ``'pandas'`` or ``'tablib'``. Defaults to ``'pandas'``.
    :raises ParserError:
    :return: a :class:`pandas.DataFrame` object
    """
    if engine == 'pandas':
        try:
            return pd.read_csv(filepath_or_buffer)
        except pd.errors.EmptyDataError:
            raise ParserError(f'Error parsing csv file due to empty data or header: {filepath_or_buffer}')
        except pd.errors.ParserError:
            raise ParserError(f'Error parsing csv file while attempting to parse: {filepath_or_buffer}')
    elif engine == 'tablib':
        try:
            with open(filepath_or_buffer, 'r') as fh:
                imported_data = tl.Dataset().load(fh)
            df = imported_data.export('df')
            return df
        except Exception:
            raise ParserError(f"Error parsing csv file: {filepath_or_buffer}")


def excel_to_dataframe(filepath_or_buffer, engine='openpyxl'):  # pragma: no cover
    """Parse an Excel file into a :class:`pandas.DataFrame`.

    :param filepath: File path
    :param engine: ``'openpyxl'``, ``'pandas'``, or ``'tablib'``.
                   Defaults to ``'openpyxl'``.
    :raises ParserError:
    :return: a :class:`pandas.DataFrame` object
    """
    if engine == 'openpyxl':
        try:
            book = pyxl.load_workbook(filepath_or_buffer)
            ws = book.active
            df = openpyxltools.ws_to_df(ws)
            return df
        except Exception:
            raise ParserError(f"Error parsing excel file: {filepath_or_buffer}")
    elif engine == 'pandas':
        try:
            df = pd.read_excel(filepath_or_buffer)
            return df
        except Exception:
            raise ParserError(f"Error parsing excel file: {filepath_or_buffer}")
    elif engine == 'tablib':
        try:
            with open(filepath_or_buffer, 'rb') as fh:
                imported_data = tl.Dataset().load(fh)
            df = imported_data.export('df')
            return df
        except Exception:
            raise ParserError(f"Error parsing excel file: {filepath_or_buffer}")
