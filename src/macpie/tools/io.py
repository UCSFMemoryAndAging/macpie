"""
Module contains tools for processing files (e.g. csv, xlsx) into DataFrames or other objects
"""

from pathlib import Path
from shutil import copy


def copy_file(orig_filepath, copy_filename):
    """Copy a file into the same directory and return filepath of copied file.

    :param orig_filepath: Filepath of file to copy
    :param copy_filename: New filename of copied file

    :return: Filepath of copied file
    """
    orig_dir = Path(orig_filepath).parent.absolute()
    copy_filepath = copy(orig_filepath, orig_dir)
    Path(copy_filepath).rename(orig_dir / copy_filename)
    copy_filepath = orig_dir / copy_filename
    return copy_filepath


def has_csv_extension(filepath):
    """Return True if ``filepath`` has an extension compatabile with
    csv files.
    """
    if filepath.suffix in set(['.csv', '.txt']):
        return True
    return False


def has_excel_extension(filepath):
    """Return True if ``filepath`` has an extension compatible with
    Excel files.
    """
    if filepath.suffix in set(['.xls', '.xlsx']):
        return True
    return False
