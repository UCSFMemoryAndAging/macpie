from pathlib import Path
from typing import Any, Optional

import click

from macpie import pathtools


def show_parameter_source(ctx, param, value):
    param_source = ctx.get_parameter_source(param.name)

    base_str = f"Parameter value for '{param.name}': "

    if param_source is click.core.ParameterSource.COMMANDLINE:
        click.echo(base_str + f"using value entered on command line [{value}].")
    if param_source is click.core.ParameterSource.ENVIRONMENT:
        click.echo(base_str + f"using value from environment variable: {param.envvar}")
    elif param_source is click.core.ParameterSource.DEFAULT:
        click.echo(base_str + f"using default value [{value}]")
    elif param_source is click.core.ParameterSource.PROMPT:
        if param.hide_input:
            click.echo(base_str + "using value entered via prompt [*****].")
        else:
            click.echo(base_str + f"using value entered via prompt [{value}].")

    return value


class ClickPath(click.Path):
    """A Click path argument that returns a ``Path``, not a string."""

    def convert(
        self,
        value: str,
        param: Optional[click.core.Parameter],
        ctx: Optional[click.core.Context],
    ) -> Any:
        """
        Return a ``Path`` from the string ``click`` would have created with
        the given options.
        """
        return Path(super().convert(value=value, param=param, ctx=ctx)).resolve(strict=True)


def allowed_path(p):
    """Determines if a filepath is considered allowed"""
    stem = p.stem
    if stem.startswith("~"):
        return False
    if pathtools.has_csv_extension(p) or pathtools.has_excel_extension(p):
        return True
    return False
