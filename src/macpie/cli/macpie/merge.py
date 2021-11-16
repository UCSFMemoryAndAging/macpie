import pathlib

import click

from macpie import read_excel, MACPieExcelWriter

from ._common import _BaseCommand


@click.command()
@click.option("--keep-original/--no-keep-original", default=True)
@click.argument(
    "primary",
    nargs=1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path),
)
@click.pass_context
def merge(ctx, keep_original, primary):
    command_meta = ctx.obj
    command_meta.command_name = ctx.info_name
    command_meta.add_opt("keep_original", keep_original)
    command_meta.add_arg("primary", primary)

    cmd = _MergeCommand(command_meta)
    cmd.run_all()


class _MergeCommand(_BaseCommand):
    def __init__(self, command_meta) -> None:
        super().__init__(command_meta)

        self.verbose = command_meta.get_opt("verbose")
        self.id_col = command_meta.get_opt("id_col")
        self.date_col = command_meta.get_opt("date_col")
        self.id2_col = command_meta.get_opt("id2_col")
        self.keep_original = command_meta.get_opt("keep_original")
        self.primary = command_meta.get_arg("primary")

    def execute(self):
        self.results = read_excel(self.primary, as_collection=True)

    def output_results(self):
        with MACPieExcelWriter(self.results_file) as writer:
            self.results.to_excel(writer, merge=True)
