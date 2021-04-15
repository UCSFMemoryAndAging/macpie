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
    if iotools.has_csv_extension(filepath):
        return csv_to_dataframe_via_pandas(filepath)
    if iotools.has_excel_extension(filepath):
        return excel_to_dataframe_via_openpyxl(filepath)
    raise ParserError(f'Error parsing file due to invalid file extension: {filepath}')


def csv_to_dataframe_via_pandas(filepath):
    try:
        return pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        raise ParserError(f'Error parsing csv file due to empty data or header: {filepath}')
    except pd.errors.ParserError:
        raise ParserError(f'Error parsing csv file while attempting to parse: {filepath}')


def csv_to_dataframe_via_tablib(filepath_or_buffer):
    try:
        with open(filepath_or_buffer, 'r') as fh:
            imported_data = tl.Dataset().load(fh)
        df = imported_data.export('df')
        return df
    except Exception:
        raise ParserError(f"Error parsing excel file: {filepath_or_buffer}")


def excel_to_dataframe_via_pandas(filepath):  # pragma: no cover
    try:
        df = pd.read_excel(filepath)
        return df
    except Exception:
        raise ParserError(f"Error parsing excel file: {filepath}")


def excel_to_dataframe_via_openpyxl(filepath):
    try:
        book = pyxl.load_workbook(filepath)
        ws = book.active
        df = openpyxltools.ws_to_df(ws)
        return df
    except Exception:
        raise ParserError(f"Error parsing excel file: {filepath}")


def excel_to_dataframe_via_tablib(filepath_or_buffer):
    try:
        with open(filepath_or_buffer, 'rb') as fh:
            imported_data = tl.Dataset().load(fh)
        df = imported_data.export('df')
        return df
    except Exception:
        raise ParserError(f"Error parsing excel file: {filepath_or_buffer}")
