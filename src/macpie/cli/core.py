from collections import namedtuple
from pathlib import Path
from typing import Any, ClassVar, Optional

import click
import pandas as pd
import openpyxl as pyxl

from macpie import __version__
from macpie.io import create_output_dir, ws_autoadjust_colwidth, ws_highlight_rows_with_col
from macpie.util import add_suffix

from .util import iterate_params


SingleSheet = namedtuple('SingleSheet', ['sheetname', 'df', 'do'])


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


class BaseResults:
    SHEETNAME_CHARS_LIMIT : ClassVar[int] = 31

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir
        self.results_dir = create_output_dir(self.output_dir, "results")
        self.results_file = self.results_dir / (self.results_dir.stem + '.xlsx')
        self.writer = pd.ExcelWriter(self.results_file, engine='openpyxl')


class CliResults(BaseResults):
    SHEETNAME_SYS_INFO: ClassVar[str] = '_sys_info'
    SHEETNAME_CLI_INFO : ClassVar[str] = '_cli_info'
    SHEETNAME_LOG_DATAOBJECTS : ClassVar[str] = '_log_dataobjects'
    SHEETNAME_LOG_OPERATIONS : ClassVar[str] = '_log_operations'

    def __init__(self, cli_ctx, output_dir: Path = None):
        self.cli_ctx = cli_ctx
        self.cli_info = self.get_cli_info()
        self.sys_info = self.get_sys_info()
        self.ws = []
        super().__init__(output_dir)

    def pre_write(self, Q):
        nodes_with_operations = Q.get_all_node_data('operation')
        for node in nodes_with_operations:
            result = node['operation_result']
            self.ws.append(SingleSheet(node['name'], result, None))

        edges_with_operation_results = Q.get_all_edge_data('operation_result')
        for edge in edges_with_operation_results:
            sheetname = edge['name']
            if edge['duplicates']:
                sheetname = add_suffix(sheetname, "(DUPS)", self.SHEETNAME_CHARS_LIMIT)
            self.ws.append(SingleSheet(sheetname, edge['operation_result'], None))

    def write(self, Q):
        self.pre_write(Q)

        for ws in self.ws:
            ws.df.to_excel(excel_writer=self.writer, sheet_name=ws[0], index=False)

        self.post_write(Q)
        self.writer.save()
        self.format_file()

    def post_write(self, Q):
        log_dataobjects = pd.DataFrame(Q.log_dataobjects)
        log_operations = pd.DataFrame(Q.log_operations)
        log_dataobjects.to_excel(excel_writer=self.writer, sheet_name=self.SHEETNAME_LOG_DATAOBJECTS, index=False)
        log_operations.to_excel(excel_writer=self.writer, sheet_name=self.SHEETNAME_LOG_OPERATIONS, index=False)
        self.cli_info.to_excel(excel_writer=self.writer, sheet_name=self.SHEETNAME_CLI_INFO, index=False)
        self.sys_info.to_excel(excel_writer=self.writer, sheet_name=self.SHEETNAME_SYS_INFO, index=False)

    def format_file(self):
        filename = str(self.results_file)
        wb = pyxl.load_workbook(filename)

        for ws in wb.worksheets:
            if ws.title.startswith('_log_'):
                ws_autoadjust_colwidth(ws)
            else:
                ws_highlight_rows_with_col(ws, '_duplicates')

        wb.save(filename)

    def get_cli_info(self):
        command = self.cli_ctx.info_name

        cli_info_columns = ['command', 'version', 'param_type', 'param_name', 'param_value']
        cli_info_data = []

        options = self.cli_ctx.obj['options']
        args = self.cli_ctx.obj['args']

        cli_info_data.extend([(command, __version__, 'option') + row for row in iterate_params(options)])
        cli_info_data.extend([(command, __version__, 'argument') + row for row in iterate_params(args)])

        return pd.DataFrame.from_records(cli_info_data, columns=cli_info_columns)

    def get_sys_info(self):
        system_info_columns = ['param_name', 'param_value']
        system_info_data = [row for row in iterate_params(self.cli_ctx.obj['system'])]
        system_info_data.append(('macpie_version', __version__))

        return pd.DataFrame.from_records(system_info_data, columns=system_info_columns)
