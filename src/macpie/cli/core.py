import functools
from pathlib import Path

import click

from macpie.tools import datetimetools, pathtools

from .helpers import get_client_system_info, get_command_info


class ResultsResource:
    def __init__(self, ctx: click.Context = None, output_dir: Path = Path("."), verbose=False):
        self.ctx = ctx if ctx is not None else click.get_current_context()
        self.sub_ctx = None
        self.output_dir = output_dir
        self.verbose = verbose
        self.results_dir = None
        self.results_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.verbose:
            click.echo("\nCOMMAND SUMMARY:\n")
            self.get_command_info().print()
            click.echo("\nSYSTEM INFO:\n")
            get_client_system_info().print()

        if self.results_file:
            click.secho(f"\nResults output to file: {self.results_file.resolve()}\n", bold=True)
        elif self.results_dir:
            click.secho(
                f"\nResults are in this directory: {self.results_dir.resolve()}\n", bold=True
            )
        elif self.output_dir:
            click.secho(
                f"\nResults are in this directory: {self.output_dir.resolve()}\n", bold=True
            )

    def create_results_dir(self):
        self.results_dir = pathtools.create_subdir(
            self.create_results_name(), where=self.output_dir
        )
        return self.results_dir

    def create_results_filepath(self, file_extension=".xlsx"):
        return self.output_dir / (self.create_results_name() + file_extension)

    def create_results_name(self):
        name_prefix = self.ctx.info_name + "_"
        if self.sub_ctx:
            name_prefix += self.sub_ctx.info_name + "_"
        return name_prefix + datetimetools.current_datetime_str()

    def get_param_value(self, param_name):
        if param_name in self.ctx.params:
            return self.ctx.params[param_name]
        if self.sub_ctx and param_name in self.sub_ctx.params:
            return self.sub_ctx.params[param_name]
        raise KeyError(f"No parameter found: {param_name}")

    def get_command_info(self):
        main_command_info = get_command_info(self.ctx)
        if self.sub_ctx:
            sub_command_info = get_command_info(self.sub_ctx)
            return main_command_info.stack(sub_command_info)
        return main_command_info


def pass_results_resource(f):
    # Decorator that passes the closest ResultsResource object to the callback,
    # setting the `sub_ctx` attribute if possible.
    def new_func(*args, **kwargs):  # type: ignore
        ctx = click.get_current_context()
        obj = ctx.find_object(ResultsResource)
        if obj is None:
            raise RuntimeError(
                "Managed to invoke callback without a context"
                f" object of type {ResultsResource.__name__!r}"
                " existing."
            )
        if ctx.parent:
            obj.sub_ctx = ctx
        return ctx.invoke(f, obj, *args, **kwargs)

    return functools.update_wrapper(new_func, f)


def allowed_path(p):
    """Determines if a filepath is considered allowed"""
    stem = p.stem
    if stem.startswith("~"):
        return False
    if pathtools.has_csv_extension(p) or pathtools.has_excel_extension(p):
        return True
    return False
