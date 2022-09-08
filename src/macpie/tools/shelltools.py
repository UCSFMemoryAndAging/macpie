import itertools
import shutil
from pathlib import Path


def copy_file_same_dir(filepath, new_file_name=None):
    """
    Copy a file into the same directory, by default appending "_copy" to
    filename, unless ``new_file_name`` is specified. This mimics behavior
    of copy and pasting a file into the same directory on a macOS, where
    multiple copies will start appending incrementing integers so the
    filename (e.g. _copy_1, _copy_2).

    Parameters
    ----------
    filepath : str, Path
        Filepath of file to copy
    new_file_name : str, default None
        New filename of copied file

    Returns
    -------
    Path
        Filepath of copied file

    Examples
    --------
    >>> copied_filepath = copy_file_same_dir('afile.csv')
    >>> copied_filepath
    PosixPath('/same/dir/afile_copy.csv')

    >>> copied_filepath = copy_file_same_dir('afile.csv')
    >>> copied_filepath
    PosixPath('/same/dir/afile_copy_2.csv')

    >>> copied_filepath = copy_file_same_dir('afile.csv', new_file_name='renamed.txt')
    >>> copied_filepath
    PosixPath('/same/dir/renamed.txt')
    """

    filepath = Path(filepath)
    if not filepath.is_file():
        raise ValueError(f"'{filepath}' is not a file.")

    file_dir = filepath.parent.absolute()
    file_stem = filepath.stem
    file_suffix = filepath.suffix

    if new_file_name:
        new_filepath = Path(file_dir / new_file_name)
        if new_filepath.exists():
            raise FileExistsError(f"{new_filepath} already exists.")
    else:
        new_file_name = file_stem + "_copy" + file_suffix
        new_filepath = Path(file_dir / new_file_name)
        if new_filepath.exists():
            for i in itertools.count(2):
                new_file_name = file_stem + "_copy_" + str(i) + file_suffix
                new_filepath = Path(file_dir / new_file_name)
                if not new_filepath.exists():
                    break

    shutil.copy(filepath, new_filepath)
    return new_filepath
