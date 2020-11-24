import click

from macpie.io import validate_filepath

from ...core import ClickPath
from ...util import allowed_file, print_ctx
from .writer import CliMergeResults


@click.command()
@click.option('--keep-original/--no-keep-original',
              default=True)
@click.argument('primary',
                nargs=1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=False))
@click.pass_context
def merge(ctx, keep_original, primary):
    options = ctx.obj['options']
    args = ctx.obj['args']

    options['keep_original'] = keep_original
    args['primary'] = validate_filepath(primary, allowed_file)

    results = CliMergeResults(ctx)
    results.write()

    click.echo(f'\nLook for results in: {results.results_file.resolve()}\n')

    if options['verbose']:
        print_ctx(ctx)
