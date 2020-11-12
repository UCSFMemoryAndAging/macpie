"""
Module contains tools for processing files (e.g. csv, xlsx) into DataFrames or other objects
"""

import openpyxl as pyxl
import pandas as pd

from macpie.exceptions import ParserError

from .excel import ws_to_df


def has_csv_extension(p):
    if p.suffix in set(['.csv', '.txt']):
        return True
    return False


def has_excel_extension(p):
    if p.suffix in set(['.xls', '.xlsx']):
        return True
    return False


def file_to_dataframe(p):
    if has_csv_extension(p):
        return csv_to_dataframe(p)
    if has_excel_extension(p):
        return excel_to_dataframe_via_openpyxl(p)
    raise ParserError(f'Error parsing file due to invalid file extension: {p}')


def csv_to_dataframe(p):
    try:
        return pd.read_csv(p)
    except pd.errors.EmptyDataError:
        raise ParserError(f'Error parsing csv file due to empty data or header: {p}')
    except pd.errors.ParserError:
        raise ParserError(f'Error parsing csv file while attempting to parse: {p}')


def excel_to_dataframe_via_pandas(p):  # pragma: no cover
    try:
        df = pd.read_excel(p, engine='openpyxl')
        return df
    except Exception:
        raise ParserError(f"Error parsing excel file: {p}")


def excel_to_dataframe_via_openpyxl(p):
    try:
        wb = pyxl.load_workbook(p)
        ws = wb.active
        df = ws_to_df(ws)
        return df
    except Exception:
        raise ParserError(f"Error parsing excel file: {p}")
