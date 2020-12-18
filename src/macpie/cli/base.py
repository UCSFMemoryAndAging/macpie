from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Optional

import click
import pandas as pd

from macpie import io
from macpie.core import Datasheet
from macpie.cli.common import get_system_info, get_version, iterate_params


class ClickPath(click.Path):
    """
    A Click path argument that returns a ``Path``, not a string.
    """

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


class CmdParams(ABC):

    @property
    @abstractmethod
    def opts(self):
        pass

    @property
    @abstractmethod
    def args(self):
        pass


class Invoker:

    SHEETNAME_COMMAND_INFO : ClassVar[str] = '_command_info'
    SHEETNAME_SYSTEM_INFO : ClassVar[str] = '_system_info'

    def __init__(self, command_name, opts, args, output_dir: Path = None):
        self.command_name = command_name
        self.opts = opts
        self.args = args

        self.output_dir = output_dir or Path('.')
        self.results_dir = io.create_output_dir(output_dir, "results")
        self.results_file = self.results_dir / (self.results_dir.stem + '.xlsx')

        self.post_messages = [f'\nLook for results in: {self.results_file.resolve()}']

    def add_opt(self, k, v):
        self.opts[k] = v

    def get_opt(self, k):
        return self.opts[k]

    def add_arg(self, k, v):
        self.args[k] = v

    def get_arg(self, k):
        return self.args[k]

    def get_command_info(self):
        cli_info_columns = ['command', 'version', 'param_type', 'param_name', 'param_value']
        cli_info_data = []
        cli_info_data.extend([(self.command_name, get_version(), 'option') + row
                              for row in iterate_params(self.opts)])
        cli_info_data.extend([(self.command_name, get_version(), 'argument') + row
                              for row in iterate_params(self.args)])
        df = pd.DataFrame.from_records(cli_info_data, columns=cli_info_columns)
        return Datasheet(self.SHEETNAME_COMMAND_INFO, df)

    def get_system_info(self):
        system_info_columns = ['param_name', 'param_value']
        system_info_data = [row for row in iterate_params(get_system_info())]
        df = pd.DataFrame.from_records(system_info_data, columns=system_info_columns)
        return Datasheet(self.SHEETNAME_SYSTEM_INFO, df)

    def add_post_message(self, msg):
        self.post_messages.append(msg)

    def print_post_messages(self):
        for msg in self.post_messages:
            click.echo(msg)
