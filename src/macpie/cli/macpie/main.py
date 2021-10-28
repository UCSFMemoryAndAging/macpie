import collections
import json
import platform
from pathlib import Path

import click

from macpie import __version__, pathtools, tablibtools, MACPieJSONEncoder
from macpie._config import get_option

from .keepone import keepone
from .link import link
from .masker import masker
from .merge import merge


class Invoker:
    def __init__(self, command_name, opts, args, output_dir: Path = Path(".")):
        self.command_name = command_name
        self.opts = opts
        self.args = args

        self.output_dir = output_dir
        self.results_dir = pathtools.create_dir_with_datetime(
            dir_name_prefix="results_", where=self.output_dir
        )
        self.results_file = self.results_dir / (self.results_dir.stem + ".xlsx")

        self.post_messages = [
            f"\nLook for results in the following directory: {self.results_dir.resolve()}"
        ]

    def add_opt(self, k, v):
        self.opts[k] = v

    def get_opt(self, k):
        return self.opts[k]

    def add_arg(self, k, v):
        self.args[k] = v

    def get_arg(self, k):
        return self.args[k]

    def get_command_info(self):
        args = {k: json.dumps(v, cls=MACPieJSONEncoder) for k, v in self.args.items()}
        opts = {k: json.dumps(v, cls=MACPieJSONEncoder) for k, v in self.opts.items()}

        info = tablibtools.DictLikeDataset(title="_mp_command_info")
        info.append(("command_name", self.command_name))
        info.append_separator("Arguments")
        info.append_dict(args)
        info.append_separator("Options")
        info.append_dict(opts)
        return info

    def get_client_system_info(self):
        info = tablibtools.DictLikeDataset(title="_mp_system_info")
        info.append(("python_version", platform.python_version()))
        info.append(("platform", platform.platform()))
        info.append(("computer_network_name", platform.node()))
        info.append(("macpie_version", __version__))
        return info

    def add_post_message(self, msg):
        self.post_messages.append(msg)

    def print_post_messages(self):
        for msg in self.post_messages:
            click.echo(msg)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-i", "--id-col", default=get_option("dataset.id_col_name"), help="ID Column Header")
@click.option(
    "-d", "--date-col", default=get_option("dataset.date_col_name"), help="Date Column Header"
)
@click.option(
    "-j", "--id2-col", default=get_option("dataset.id2_col_name"), help="ID2 Column Header"
)
@click.version_option(__version__)
@click.pass_context
def main(ctx, verbose, id_col, date_col, id2_col):
    command_name = ctx.info_name
    opts = collections.OrderedDict()
    args = collections.OrderedDict()

    opts["verbose"] = verbose
    opts["id_col"] = id_col
    opts["date_col"] = date_col
    opts["id2_col"] = id2_col

    invoker = Invoker(command_name, opts, args)
    ctx.obj = invoker

    @ctx.call_on_close
    def on_close():
        if verbose:
            click.echo("\nCOMMAND SUMMARY:\n")
            invoker.get_command_info().print()
            click.echo("\nSYSTEM INFO:\n")
            invoker.get_client_system_info().print()
        invoker.print_post_messages()


main.add_command(keepone)
main.add_command(link)
main.add_command(masker)
main.add_command(merge)
