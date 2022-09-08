"""Path utilities"""

from pathlib import Path
from typing import Callable, List, Tuple

from macpie.tools import datetimetools, lltools


def create_dir_with_datetime(dir_name_prefix="new_folder_", where=Path(".")):
    """Create a new directory with the current datetime appended."""
    new_dir_name = dir_name_prefix + datetimetools.current_datetime_str()
    return create_subdir(new_dir_name, where=where)


def create_subdir(subdir_name: str, where=Path("."), exists_ok=False):
    """Creates a sub directory with the current date/time appended to
    the directory name.

        >>> from pathlib import Path
        >>> results_dir = pathtools.create_subdir(Path('.'), "results")
        >>> results_dir
        PosixPath('results_20210521_162611')

    :param output_dir: Directory in which to create the new directory.
                       Defaults to None, which will use the current directory.
    :param output_dir_name: Name of the new directory.
                            Defaults to None, which will use "new_folder".
    """
    final_dir = where / subdir_name
    final_dir.mkdir(exist_ok=exists_ok)
    return final_dir


def get_files_from_dir(d: Path) -> List[Path]:
    """Get all files only from directory

    :param d: directory

    :return: list of files
    """

    # Note that Path.iterdir() yields path objects in arbitrary order
    return [f.resolve() for f in Path(d).iterdir() if f.is_file()]


def has_csv_extension(filepath):
    """Return True if ``filepath`` has an extension compatabile with
    csv files.
    """
    if filepath.suffix in set([".csv", ".txt"]):
        return True
    return False


def has_excel_extension(filepath):
    """Return True if ``filepath`` has an extension compatible with
    Excel files.
    """
    if filepath.suffix in set([".xls", ".xlsx"]):
        return True
    return False


def validate_paths(
    ps: List[Path],
    allowed_path: Callable = None,
    recurse=True,
    ignore_dot=True,
    ignore_tilde=True,
) -> Tuple[list, list]:

    to_validate = []
    valid = []
    invalid = []

    for p in ps:
        if p.is_dir() and recurse:
            to_validate.extend(get_files_from_dir(p))
        else:
            to_validate.append(p.resolve())

    to_validate = lltools.remove_duplicates(to_validate)
    for p in to_validate:
        if p.stem.startswith(".") and ignore_dot:
            continue
        if p.stem.startswith("~") and ignore_tilde:
            continue
        if allowed_path and not allowed_path(p):
            invalid.append(p)
            continue

        if p.is_file():
            valid.append(p)
        else:
            invalid.append(p)

    return (valid, invalid)
