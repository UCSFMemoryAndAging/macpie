"""
Module contains tools for processing files (e.g. csv, xlsx) into DataFrames or other objects
"""

from pathlib import Path
from shutil import copy


def copy_file(orig_filepath, copy_filename):
    orig_dir = Path(orig_filepath).parent.absolute()
    copy_filepath = copy(orig_filepath, orig_dir)
    Path(copy_filepath).rename(orig_dir / copy_filename)
    copy_filepath = orig_dir / copy_filename
    return copy_filepath


def has_csv_extension(filepath):
    if filepath.suffix in set(['.csv', '.txt']):
        return True
    return False


def has_excel_extension(filepath):
    if filepath.suffix in set(['.xls', '.xlsx']):
        return True
    return False
