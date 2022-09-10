import json
import platform
from functools import update_wrapper

import click

from macpie import __version__, tablibtools, MACPieExcelWriter, MACPieJSONEncoder


class SingletonExcelWriter:
    def __init__(self, path, *args, **kwargs):
        class singleton_excel_writer:
            instance = None

            def __new__(cls):
                if cls.instance is None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    cls.instance = MACPieExcelWriter(
                        path,
                        *args,
                        **kwargs,
                    )
                return cls.instance

        self.singleton_class = singleton_excel_writer

    def __enter__(self):
        return self.singleton_class

    def __exit__(self, exc_type, exc_value, tb):
        if self.singleton_class.instance is not None:
            self.singleton_class().close()


def get_all_commands(ctx: click.Context):
    parent_cmd = ctx.command
    sub_cmds = []
    if isinstance(parent_cmd, click.MultiCommand):
        sub_cmds = [
            parent_cmd.get_command(ctx, sub_cmd_name)
            for sub_cmd_name in parent_cmd.list_commands(ctx)
        ]
    return parent_cmd, sub_cmds


def get_client_system_info():
    info = tablibtools.MacpieTablibDataset(title="_mp_system_info")
    info.headers = ("client_info_name", "client_info_value")
    info.append(("python_version", platform.python_version()))
    info.append(("platform", platform.platform()))
    info.append(("computer_network_name", platform.node()))
    info.append(("macpie_version", __version__))
    return info


def get_command_info(ctx: click.Context):
    info = tablibtools.MacpieTablibDataset(title="_mp_command_info")
    info.headers = (
        "commmand",
        "parameter_name",
        "parameter_type",
        "parameter_source",
        "parameter_value",
    )
    for param, param_source, param_value in get_param_values(ctx):
        info.append(
            (
                ctx.info_name,
                param.name,
                type(param).__name__,
                param_source.name,
                json.dumps(param_value, cls=MACPieJSONEncoder),
            )
        )
    return info


def get_command_option_params(command):
    for param in command.params:
        if isinstance(param, click.Option):
            yield param


def get_param_values(ctx):
    for param in ctx.command.params:
        if param.name in ctx.params:
            param_source = ctx.get_parameter_source(param.name)
            param_value = ctx.params[param.name]
            yield param, param_source, param_value


def pipeline_generator(f):
    """Similar to the :func:`pipeline_processor` but passes through old values
    unchanged and does not pass through the values as parameter.

    From: https://github.com/pallets/click/blob/fb4327216543d751e2654a0d3bf6ce3d31c435cc/examples/imagepipe/imagepipe.py
    """

    @pipeline_processor
    def new_func(stream, *args, **kwargs):
        yield from stream
        yield from f(*args, **kwargs)

    return update_wrapper(new_func, f)


def pipeline_processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.

    From: https://github.com/pallets/click/blob/fb4327216543d751e2654a0d3bf6ce3d31c435cc/examples/imagepipe/imagepipe.py
    """

    def new_func(*args, **kwargs):
        def processor(stream):
            return f(stream, *args, **kwargs)

        return processor

    return update_wrapper(new_func, f)
