import click

from macpie.classes import Query
from macpie.io import validate_filepath

from ...core import ClickPath
from ...util import allowed_file, print_ctx
from .writer import CliMergeResults


@click.command()
@click.option('-k', '--keep',
              default='all',
              type=click.Choice(['all', 'first', 'latest'], case_sensitive=False))
@click.argument('primary',
                nargs=1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=False))
@click.pass_context
def merge(ctx, keep, primary):
    options = ctx.obj['options']
    args = ctx.obj['args']

    options['keep'] = keep
    args['primary'] = primary

    _primary = validate_filepath(primary, allowed_file)

    Q = Query()

    click.echo("Executing query...")
    Q.execute()
    click.echo("Writing query results...")

    results = CliMergeResults(ctx)
    results.write()

    click.echo(f'\nLook for results in: {results.results_file.resolve()}\n')

    if options['verbose']:
        print_ctx(ctx)
