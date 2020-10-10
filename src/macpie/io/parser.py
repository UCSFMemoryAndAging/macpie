"""
Module contains tools for processing files (e.g. csv, xlsx) into DataFrames or other objects
"""

import openpyxl as pyxl
import pandas as pd

from macpie.exceptions import FileImportError


# allowed file extensions
ALLOWED_CSV_EXTENSIONS = set(['.csv', '.txt'])
ALLOWED_EXCEL_EXTENSIONS = set(['.xls', '.xlsx'])
ALLOWED_EXTENSIONS = ALLOWED_CSV_EXTENSIONS | ALLOWED_EXCEL_EXTENSIONS


def allowed_file(p):
    """Determines if a file is considered allowed
    :return: ``True`` if a file has an extension specified in ALLOWED_EXTENSIONS set.
    """
    stem = p.stem
    if stem.startswith('~') or stem.startswith('results_'):
        return False
    if p.suffix not in ALLOWED_EXTENSIONS:
        return False
    return True


def import_file(p):
    suffix = p.suffix
    if suffix in ALLOWED_CSV_EXTENSIONS:
        return _import_csv(p)
    elif suffix in ALLOWED_EXCEL_EXTENSIONS:
        return _import_xl_via_openpyxl(p)
    raise FileImportError(f'Error importing file due to invalid file extension: {p}')


def _import_csv(p):
    try:
        return pd.read_csv(p)
    except pd.errors.EmptyDataError:
        raise FileImportError(f'Error importing csv file due to empty data or header: {p}')
    except pd.errors.ParserError:
        raise FileImportError(f'Error importing csv file while attempting to parse: {p}')


def _import_xl_via_pandas(p):  # pragma: no cover
    try:
        df = pd.read_excel(p, engine='openpyxl')
        return df
    except Exception:
        raise FileImportError(f"Error importing excel file: {p}")


def _import_xl_via_openpyxl(p):
    try:
        wb = pyxl.load_workbook(p)
        ws = wb.active
        df = _convert_xlws_to_df(ws)
        return df
    except Exception:
        raise FileImportError(f"Error importing excel file: {p}")


def _convert_xlws_to_df(ws):
    data = ws.values
    cols = next(data)
    df = pd.DataFrame(data, columns=cols)
    return df
