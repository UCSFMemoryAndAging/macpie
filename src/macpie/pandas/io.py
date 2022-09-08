"""
Module contains tools for processing files (e.g. csv, xlsx) into pandas objects
"""
import pandas as pd
import tablib as tl

from macpie.core.exceptions import UnsupportedFormat
from macpie.io.utils import detect_format
from macpie.tools import openpyxltools, tablibtools


def read_file(
    filepath_or_buffer,
    format_options={
        "csv": {"engine": "pandas", "engine_kwargs": {}},
        "xlsx": {"engine": "pandas", "engine_kwargs": {}},
    },
):
    """
    Parse a file into a :class:`pandas.DataFrame`.

    Parameters
    ----------
    filepath_or_buffer : various
        File path or file-like object

    Returns
    -------
    DataFrame
    """
    fmt = detect_format(filepath_or_buffer)

    if fmt in ("csv", "tsv"):
        csv_options = format_options.pop("csv", {})
        csv_engine = csv_options.pop("engine", "pandas")
        csv_engine_kwargs = csv_options.pop("engine_kwargs", {})
        csv_engine_kwargs["delimiter"] = "\t" if fmt == "tsv" else ","

        return read_csv(filepath_or_buffer, engine=csv_engine, engine_kwargs=csv_engine_kwargs)

    if fmt == "xlsx":
        xlsx_options = format_options.pop("xlsx", {})
        xlsx_engine = xlsx_options.pop("engine", "pandas")
        xlsx_engine_kwargs = xlsx_options.pop("engine_kwargs", {})
        return read_excel(filepath_or_buffer, engine=xlsx_engine, engine_kwargs=xlsx_engine_kwargs)

    raise UnsupportedFormat(f"File with this format not supported: {filepath_or_buffer}")


def read_csv(filepath_or_buffer, engine="pandas", engine_kwargs={}):
    """
    Parse a csv file into a :class:`pandas.DataFrame`.

    Parameters
    ----------
    filepath : various
        File path or file-like object
    engine :  {'pandas', 'tablib'}, default 'pandas'
        Parser engine to use.

    Returns
    -------
    DataFrame
    """

    delimiter = engine_kwargs.pop("delimiter")

    if engine == "pandas":
        return pd.read_csv(filepath_or_buffer, delimiter=delimiter, **engine_kwargs)

    if engine == "tablib":
        with open(filepath_or_buffer, "r") as fh:
            imported_data = tl.Dataset().load(fh, delimiter=delimiter, **engine_kwargs)
        return imported_data.export("df")


def read_excel(filepath_or_buffer, sheet_name=None, engine="pandas", engine_kwargs={}):
    """
    Parse an Excel file into a :class:`pandas.DataFrame`.

    Parameters
    ----------
    filepath_or_buffer : various
        File path or file-like object
    sheet_name : str, optional
        Worksheet to parse. If not specified, active worksheet is parsed.
    engine :  {'openpyxl', 'pandas', 'tablib'}, default 'openpyxl'
        Parser engine to use.

    Returns
    -------
    DataFrame
    """
    sheet_name = engine_kwargs.pop("sheet_name", sheet_name)

    if engine == "pandas":
        if sheet_name is None:
            sheet_name = 0
        return pd.read_excel(filepath_or_buffer, sheet_name=sheet_name, **engine_kwargs)

    if engine == "tablib":
        tlset = tablibtools.read_excel(filepath_or_buffer, sheet_name=sheet_name, **engine_kwargs)
        return tlset.export("df")

    if engine == "openpyxl":
        return openpyxltools.file_to_dataframe(
            filepath_or_buffer, sheet_name=sheet_name, **engine_kwargs
        )
