import shutil
from pathlib import Path


def copy_file(orig_filepath, copy_filename):
    """Copy a file into the same directory and return filepath of copied file.

    :param orig_filepath: Filepath of file to copy
    :param copy_filename: New filename of copied file

    :return: Filepath of copied file
    """
    orig_dir = Path(orig_filepath).parent.absolute()
    copy_filepath = shutil.copy(orig_filepath, orig_dir)
    Path(copy_filepath).rename(orig_dir / copy_filename)
    copy_filepath = orig_dir / copy_filename
    return copy_filepath
