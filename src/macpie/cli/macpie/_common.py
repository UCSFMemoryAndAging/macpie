import abc
import collections
import json
import platform
from pathlib import Path

import click

from macpie import __version__, pathtools, tablibtools, MACPieJSONEncoder
from macpie._config import get_option


class CommandMeta:
    def __init__(self, command_name, output_dir: Path = Path(".")):
        self.command_name = command_name
        self.output_dir = output_dir

        self.opts = collections.OrderedDict()
        self.args = collections.OrderedDict()

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


class _BaseCommand(abc.ABC):
    def __init__(self, command_meta):
        self.command_meta = command_meta

        self.results_dir = None
        self.results_file = None

        self.post_messages = []

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def output_results(self):
        pass

    def run_all(self):
        self.execute()
        self.prepare_output()
        self.output_results()
        self.print_post_messages()

    def prepare_output(self):
        self.results_dir = pathtools.create_dir_with_datetime(
            dir_name_prefix="results_", where=self.command_meta.output_dir
        )
        self.results_file = self.results_dir / (self.results_dir.stem + ".xlsx")

    def print_post_messages(self):
        if self.command_meta.get_opt("verbose") is True:
            click.echo("\nCOMMAND SUMMARY:\n")
            self.command_meta.get_command_info().print()
            click.echo("\nSYSTEM INFO:\n")
            self.command_meta.get_client_system_info().print()

        click.echo(f"\nLook for results in the following directory: {self.results_dir.resolve()}")
