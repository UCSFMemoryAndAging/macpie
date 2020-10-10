"""Common IO api utilities"""

from pathlib import Path

from macpie.exceptions import WriteError
from macpie.util import append_current_datetime_str


def create_output_dir(p: Path = None):
    if p is None:
        p = Path('.')

    try:
        if not p.is_dir():
            raise WriteError(f'Error writing output. Path is not a valid directory: {p}')
    except Exception:
        raise WriteError(f'Error writing output. Path is not a valid path: {p}')

    new_dir = append_current_datetime_str("results")
    final_dir = p / new_dir
    final_dir.mkdir(exist_ok=False)

    return final_dir


def get_files_from_dir(p):
    """Gets files only from a specified path
    :return: list of files
    """
    return [f.resolve() for f in Path(p).iterdir() if f.is_file()]
