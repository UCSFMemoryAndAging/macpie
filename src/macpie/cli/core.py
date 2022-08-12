import functools
from pathlib import Path
from webbrowser import get

import click

from macpie import pathtools

from .helpers import get_client_system_info, get_command_info


class ResultsResource:
    def __init__(self, ctx: click.Context = None, output_dir: Path = Path("."), verbose=False):
        self.output_dir = output_dir
        self.results_dir = pathtools.create_dir_with_datetime(
            dir_name_prefix="results_", where=output_dir
        )
        self.results_file = self.results_dir / (self.results_dir.stem + ".xlsx")
        self.verbose = verbose
        self.ctx = ctx if ctx is not None else click.get_current_context()
        self.sub_ctx = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.verbose:
            click.echo("\nCOMMAND SUMMARY:\n")
            get_command_info(self.ctx).print()
            if self.sub_ctx:
                get_command_info(self.sub_ctx).print()
            click.echo("\nSYSTEM INFO:\n")
            get_client_system_info().print()

        click.echo(f"\nLook for results in the following directory: {self.output_dir.resolve()}")

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


def make_pass_results_resource():
    """Given an object type this creates a decorator that will work
    similar to :func:`pass_obj` but instead of passing the object of the
    current context, it will find the innermost context of type
    :func:`object_type`.

    This generates a decorator that works roughly like this::

        from functools import update_wrapper

        def decorator(f):
            @pass_context
            def new_func(ctx, *args, **kwargs):
                obj = ctx.find_object(object_type)
                return ctx.invoke(f, obj, *args, **kwargs)
            return update_wrapper(new_func, f)
        return decorator

    :param object_type: the type of the object to pass.
    :param ensure: if set to `True`, a new object will be created and
                   remembered on the context if it's not there yet.
    """

    def decorator(f):
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

    return decorator


# decorator to pass the ResultsResource object
pass_results_resource = make_pass_results_resource()


def allowed_path(p):
    """Determines if a filepath is considered allowed"""
    stem = p.stem
    if stem.startswith("~"):
        return False
    if pathtools.has_csv_extension(p) or pathtools.has_excel_extension(p):
        return True
    return False
