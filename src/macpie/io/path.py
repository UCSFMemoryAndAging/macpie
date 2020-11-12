"""Path utilities"""

from pathlib import Path
from typing import Callable

from macpie.exceptions import PathError
from macpie.util import append_current_datetime_str


def create_output_dir(output_dir: Path = None, output_dir_name: str = None):
    if output_dir is None:
        output_dir = Path('.')

    try:
        if not output_dir.is_dir():
            raise PathError(f'Error writing output. Path is not a valid directory: {output_dir}')
    except Exception:
        raise PathError(f'Error writing output. Path is not a valid path: {output_dir}')

    if output_dir_name is None:
        output_dir_name = append_current_datetime_str("new_folder")
    else:
        output_dir_name = append_current_datetime_str(output_dir_name)

    final_dir = output_dir / output_dir_name
    final_dir.mkdir(exist_ok=False)

    return final_dir


def get_files_from_dir(p):
    """Gets files only from a specified path
    :return: list of files
    """
    return [f.resolve() for f in Path(p).iterdir() if f.is_file()]


def validate_filepath(p, allowed_file: Callable = None):
    if not p.exists():
        raise PathError('ERROR: File does not exist.')
    if p.is_dir():
        raise PathError('ERROR: File is not a file but a directory.')
    if allowed_file is not None:
        if not allowed_file(p):
            raise PathError('ERROR: File is specified as not allowed.')
    return p


def validate_filepaths(ps, allowed_file: Callable = None):
    """ps should be an iterable, like a list of files"""

    if allowed_file is None:
        def allowed_file(p):
            return True

    to_validate = []
    valid = []
    invalid = []

    for p in ps:
        if p.is_dir():
            to_validate.extend(get_files_from_dir(p))
        else:
            to_validate.append(p)

    for p in to_validate:
        if p in valid or p in invalid:
            continue
        try:
            vp = validate_filepath(p, allowed_file)
            valid.append(vp)
        except PathError:
            invalid.append(p)

    return (valid, invalid)
