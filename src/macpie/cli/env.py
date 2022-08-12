import os
from pathlib import Path

import click

from .helpers import get_all_commands, get_command_option_params


def create_envfile(ctx: click.Context, overwrite=False):
    env_filename = "." + ctx.parent.auto_envvar_prefix.lower() + "env"
    env_filepath = Path(Path.home() / env_filename)
    if not overwrite and env_filepath.exists():
        raise click.UsageError(
            f"ERROR: env file already exists: {env_filepath}. Use '--overwrite' option to overwrite file."
        )

    with open(env_filepath, "w") as f:
        for envvar_name, option in get_auto_envvars(ctx.parent):
            opts, help = option.get_help_record(ctx)

            default_value = option.get_default(ctx, call=True)
            if isinstance(default_value, (list, tuple)):
                default_value = f'"{" ".join(str(d) for d in default_value)}"'
            else:
                default_value = str(default_value)

            f.write("# " + opts + "\n")
            if help:
                f.write("# " + help + "\n")
            f.write(envvar_name + " = " + default_value + "\n\n")


def get_auto_envvars(ctx: click.Context):
    parent_cmd, sub_cmds = get_all_commands(ctx)
    for option in get_command_option_params(parent_cmd):
        envvar_name = "_".join([ctx.auto_envvar_prefix, option.name]).upper()
        yield (envvar_name, option)
    for sub_cmd in sub_cmds:
        for option in get_command_option_params(sub_cmd):
            envvar_name = "_".join([ctx.auto_envvar_prefix, sub_cmd.name, option.name]).upper()
            yield (envvar_name, option)


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
    env_filepath = Path(Path.home() / env_filename)

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


def overwrite_envfile_option(func):
    func = click.option(
        "--overwrite",
        is_flag=True,
        help="Whether to overwrite existing env file if it exists.",
    )(func)
    return func
