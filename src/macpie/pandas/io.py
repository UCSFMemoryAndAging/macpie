"""
Module contains tools for processing files (e.g. csv, xlsx) into pandas objects
"""

import openpyxl as pyxl
import pandas as pd
import tablib as tl

from macpie import openpyxltools, pathtools


def file_to_dataframe(filepath):
    """Parse a file into a :class:`pandas.DataFrame`.

    :param filepath: File path
    :return: a :class:`pandas.DataFrame` object
    """
    if pathtools.has_csv_extension(filepath):
        return csv_to_dataframe(filepath, engine="pandas")
    if pathtools.has_excel_extension(filepath):
        return excel_to_dataframe(filepath, engine="openpyxl")
    raise NotImplementedError(f"Parsing file with this extension not implemented: {filepath}")


def csv_to_dataframe(filepath_or_buffer, engine="pandas"):
    """Parse a csv file into a :class:`pandas.DataFrame`.

    :param filepath: File path
    :param engine: ``'pandas'`` or ``'tablib'``. Defaults to ``'pandas'``.
    :return: a :class:`pandas.DataFrame` object
    """
    if engine == "pandas":
        return pd.read_csv(filepath_or_buffer)
    elif engine == "tablib":
        with open(filepath_or_buffer, "r") as fh:
            imported_data = tl.Dataset().load(fh)
        df = imported_data.export("df")
        return df


def excel_to_dataframe(filepath_or_buffer, sheet_name=None, engine="openpyxl"):  # pragma: no cover
    """Parse an Excel file into a :class:`pandas.DataFrame`.

    :param filepath: File path
    :param engine: ``'openpyxl'``, ``'pandas'``, or ``'tablib'``.
                   Defaults to ``'openpyxl'``.
    :return: a :class:`pandas.DataFrame` object
    """
    if engine == "openpyxl":
        book = pyxl.load_workbook(filepath_or_buffer, read_only=True, data_only=True)
        if sheet_name is None:
            ws = book.active
        else:
            ws = book[sheet_name]
        df = openpyxltools.to_df(ws)
        return df
    elif engine == "pandas":
        if sheet_name is None:
            sheet_name = 0
        df = pd.read_excel(filepath_or_buffer, sheet_name=sheet_name)
        return df
    elif engine == "tablib":
        with open(filepath_or_buffer, "rb") as fh:
            imported_data = tl.Dataset().load(fh)
        df = imported_data.export("df")
        return df
