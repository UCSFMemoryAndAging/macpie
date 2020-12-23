"""Path utilities"""

from pathlib import Path
from typing import Callable, List, Tuple

from macpie import errors, util


def create_output_dir(output_dir: Path = None, output_dir_name: str = None):
    if output_dir is None:
        output_dir = Path('.')

    try:
        if not output_dir.is_dir():
            raise errors.PathError(f'Error writing output. Path is not a valid directory: {output_dir}')
    except Exception:
        raise errors.PathError(f'Error writing output. Path is not a valid path: {output_dir}')

    if output_dir_name is None:
        output_dir_name = util.datetime.append_current_datetime_str("new_folder")
    else:
        output_dir_name = util.datetime.append_current_datetime_str(output_dir_name)

    final_dir = output_dir / output_dir_name
    final_dir.mkdir(exist_ok=False)

    return final_dir


def get_files_from_dir(d: Path) -> List[Path]:
    """
    Get all files only from directory

    :param d: directory

    :return: list of files
    """
    return [f.resolve() for f in Path(d).iterdir() if f.is_file()]


def validate_filepath(p: Path, allowed_file: Callable = None) -> Path:
    """
    Validate a path to a file.

    :param p: file path
    :param allowed_file: a function that returns True if considered valid

    :return: file path is valid

    :raises: :class:`macpie.errors.PathError` if file doesn't exist,
             is a directory, or not allowed in ``allowed_file``
    """
    if not p.exists():
        raise errors.PathError('ERROR: File does not exist.')
    if p.is_dir():
        raise errors.PathError('ERROR: File is not a file but a directory.')
    if allowed_file is not None:
        if not allowed_file(p):
            raise errors.PathError('ERROR: File is specified as not allowed.')
    return p


def validate_filepaths(ps: [Path], allowed_file: Callable = None) -> Tuple[list, list]:
    """
    Validate a container of file paths.

    :param ps: container of file paths
    :param allowed_file: a function that returns True if considered valid

    :return: Length-2 tuple where the first element is list of valid files,
             and second element is list of invliad files.
    """
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
        # ignore hidden files
        if p.stem.startswith('.'):
            continue
        # ignore temp excel files
        if p.stem.startswith('~') and p.suffix.startswith('.xls'):
            continue
        try:
            vp = validate_filepath(p, allowed_file)
            valid.append(vp)
        except errors.PathError:
            invalid.append(p)

    return (valid, invalid)
