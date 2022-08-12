import json
import platform

import click

from macpie import __version__, tablibtools, MACPieJSONEncoder


def get_client_system_info():
    info = tablibtools.DictLikeDataset(title="_mp_system_info")
    info.append(("python_version", platform.python_version()))
    info.append(("platform", platform.platform()))
    info.append(("computer_network_name", platform.node()))
    info.append(("macpie_version", __version__))
    return info


def get_command_info(ctx: click.Context):
    opts = {
        param_name: json.dumps(param_value, cls=MACPieJSONEncoder)
        for param_name, param_value in get_option_values(ctx)
    }
    args = {
        param_name: json.dumps(param_value, cls=MACPieJSONEncoder)
        for param_name, param_value in get_argument_values(ctx)
    }

    info = tablibtools.DictLikeDataset(title="_mp_command_info")
    info.append(("command_name", ctx.info_name))
    info.append_separator("Arguments")
    info.append_dict(args)
    info.append_separator("Options")
    info.append_dict(opts)
    return info


def get_all_commands(ctx: click.Context):
    parent_cmd = ctx.parent.command
    sub_cmds = []
    if isinstance(parent_cmd, click.MultiCommand):
        sub_cmd_names = parent_cmd.list_commands(ctx.parent)
        sub_cmds = [
            parent_cmd.get_command(ctx.parent, cmd_name=sub_cmd_name)
            for sub_cmd_name in sub_cmd_names
        ]
    return parent_cmd, sub_cmds


def get_command_option_params(command):
    for param in command.params:
        if isinstance(param, click.Option):
            yield param


def get_option_values(ctx: click.Context):
    for option in get_command_option_params(ctx.command):
        if option.name in ctx.params:
            param_source = ctx.get_parameter_source(option.name)
            yield (option.name, str(ctx.params[option.name]) + " (" + str(param_source) + ")")


def get_command_argument_params(command):
    for param in command.params:
        if isinstance(param, click.Argument):
            yield param


def get_argument_values(ctx: click.Context):
    for argument in get_command_argument_params(ctx.command):
        yield (argument.name, ctx.params[argument.name])
