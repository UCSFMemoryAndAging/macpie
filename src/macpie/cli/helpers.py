import json
import platform

import click

from macpie import __version__, tablibtools, MACPieJSONEncoder


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
