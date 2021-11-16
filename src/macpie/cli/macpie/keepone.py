import pathlib

import click

from macpie import BasicList, Dataset, MACPieExcelWriter, pathtools
from macpie._config import get_option
from macpie.cli.common import allowed_path

from ._common import _BaseCommand


@click.command()
@click.option(
    "-k",
    "--keep",
    default="all",
    type=click.Choice(
        ["all", "earliest", "latest"],
        case_sensitive=False,
    ),
)
@click.argument(
    "primary",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=pathlib.Path),
)
@click.pass_context
def keepone(ctx, keep, primary):
    """
    This command groups rows that have the same :option:`--id2-col` value, and allows you to keep
    only the earliest or latest row in each group as determined by the :option:`--date-col` values
    (discarding the other rows in the group).

    primary : pathlib.Path
        a file path

    """
    command_meta = ctx.obj
    command_meta.command_name = ctx.info_name
    command_meta.add_opt("keep", keep)
    command_meta.add_arg("primary", primary)

    cmd = _KeepOneCommand(command_meta)
    cmd.run_all()


class _KeepOneCommand(_BaseCommand):
    def __init__(self, command_meta) -> None:
        super().__init__(command_meta)

        self.verbose = command_meta.get_opt("verbose")
        self.id_col = command_meta.get_opt("id_col")
        self.date_col = command_meta.get_opt("date_col")
        self.id2_col = command_meta.get_opt("id2_col")
        self.keep = command_meta.get_opt("keep")
        self.primary = command_meta.get_arg("primary")

        self._validate()

    def execute(self):
        collection = BasicList()

        for filepath in self.primary:
            dset = Dataset.from_file(
                filepath,
                id_col_name=self.id_col,
                date_col_name=self.date_col,
                id2_col_name=self.id2_col,
                name=filepath.stem,
            )

            dset = dset.group_by_keep_one(keep=self.keep, drop_duplicates=False)

            if get_option("column.system.duplicates") in dset.columns:
                dset.add_tag(Dataset.tag_duplicates)

            collection.append(dset)

        self.results = collection

    def output_results(self):
        with MACPieExcelWriter(self.results_file) as writer:
            self.results.to_excel(writer)
            self.command_meta.get_command_info().to_excel(writer)
            self.command_meta.get_client_system_info().to_excel(writer)

    def _validate(self):
        primary_valid, primary_invalid = pathtools.validate_paths(self.primary, allowed_path)

        for p in primary_invalid:
            click.echo(f"WARNING: Ignoring invalid file: {p}")

        if len(primary_valid) < 1:
            raise click.UsageError("ERROR: No valid files.")

        self.primary = primary_valid
