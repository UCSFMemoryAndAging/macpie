import pathlib
import os

import click


def get_load_dotenv(command: str = "MACPIE", default: bool = True) -> bool:
    """Get whether the user has disabled loading default dotenv file for
    a specific command by setting "``command``_SKIP_DOTENV".
    The default is ``True``, load the files.

    Parameters
    ----------
    default : bool, default True
        What to return if the env var isn't set.
    """
    val = os.environ.get(command.upper() + "_SKIP_DOTENV")

    if not val:
        return default

    return val.lower() in ("0", "false", "no")


def load_dotenv(command: str = "MACPIE") -> bool:
    """Load "dotenv" file for a specific command.

    If an env var is already set it is not overwritten.

    This is a no-op if `python-dotenv`_ is not installed.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    Returns
    -------
    ``True`` if the env file was loaded.
    """

    env_filename = "." + command.lower() + "env"
    env_filepath = pathlib.Path(pathlib.Path.home() / env_filename)

    try:
        import dotenv
    except ImportError:
        if env_filepath.is_file():
            click.secho(
                f" * Tip: There is an env file '{env_filename}' present."
                ' Do "pip install python-dotenv" to use it.',
                fg="yellow",
                err=True,
            )

        return False

    if env_filepath.is_file():
        return dotenv.load_dotenv(env_filepath, encoding="utf-8")
    return False
