from functools import partial

import click

from macpie.classes import LavaDataObject, Query
from macpie.io import validate_filepaths
from macpie.pandas import group_by_keep_one

from ...core import ClickPath, CliResults
from ...util import allowed_file, print_ctx


@click.command()
@click.option('-k', '--keep',
              default='all',
              type=click.Choice(['all', 'first', 'latest'], case_sensitive=False))
@click.argument('primary',
                nargs=-1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.pass_context
def keepone(ctx, keep, primary):
    options = ctx.obj['options']
    args = ctx.obj['args']

    options['keep'] = keep
    args['primary'] = primary

    _primary_valid, _primary_invalid = validate_filepaths(primary, allowed_file)

    for p in _primary_invalid:
        click.echo(f"WARNING: Ignoring invalid file: {p}")

    if len(_primary_valid) < 1:
        raise click.UsageError("ERROR: No valid files.")

    Q = Query()

    for prim in _primary_valid:
        primary_do = LavaDataObject.from_file(
            prim,
            prim.stem,
            id_col=options['id_col'],
            date_col=options['date_col'],
            id2_col=options['id2_col']
        )

        Q.add_node(
            primary_do,
            operation=partial(group_by_keep_one,
                              group_by_col=primary_do.id2_col,
                              date_col=primary_do.date_col,
                              keep=options['keep'],
                              drop_duplicates=False)
        )

    click.echo("Executing query...")
    Q.execute()
    click.echo("Writing query results...")

    results = CliResults(ctx)
    results.write(Q)

    click.echo(f'\nLook for results in: {results.results_file.resolve()}\n')

    if options['verbose']:
        print_ctx(ctx)
