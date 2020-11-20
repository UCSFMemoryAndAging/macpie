from functools import partial

import click

from macpie.classes import LavaDataObject, Query
from macpie.exceptions import DataObjectIDColKeyError, ParserError
from macpie.io import validate_filepath, validate_filepaths
from macpie.pandas import date_proximity, group_by_keep_one

from ...core import ClickPath
from .writer import CliLinkResults
from ...util import allowed_file, print_ctx


@click.command()
@click.option('-k', '--primary-keep',
              default='all',
              type=click.Choice(['all', 'first', 'latest'], case_sensitive=False))
@click.option('-g', '--secondary-get',
              default='all',
              type=click.Choice(['all', 'closest'], case_sensitive=False))
@click.option('-t', '--secondary-days',
              default=90)
@click.option('-w', '--secondary-when',
              default='earlier_or_later',
              type=click.Choice(['earlier', 'later', 'earlier_or_later'], case_sensitive=False))
@click.option('-i', '--secondary-id-col',
              default=None,
              help="Secondary ID Column Header")
@click.option('-d', '--secondary-date-col',
              default=None,
              help="Secondary Date Column Header")
@click.option('-j', '--secondary-id2-col',
              default=None,
              help="Secondary ID2 Column Header")
@click.option('--merge-results/--no-merge-results',
              default=True)
@click.option('--keep-original/--no-keep-original',
              default=False)
@click.argument('primary',
                nargs=1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.argument('secondary',
                nargs=-1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.pass_context
def link(ctx,
         primary_keep,
         secondary_get,
         secondary_days,
         secondary_when,
         secondary_id_col,
         secondary_date_col,
         secondary_id2_col,
         merge_results,
         keep_original,
         primary,
         secondary):

    options = ctx.obj['options']
    args = ctx.obj['args']

    options['primary_keep'] = primary_keep
    options['secondary_get'] = secondary_get
    options['secondary_days'] = secondary_days
    options['secondary_when'] = secondary_when
    options['secondary_id_col'] = secondary_id_col if secondary_id_col is not None else options['id_col']
    options['secondary_date_col'] = secondary_date_col if secondary_date_col is not None else options['date_col']
    options['secondary_id2_col'] = secondary_id2_col if secondary_id2_col is not None else options['id2_col']
    options['merge_results'] = merge_results
    options['keep_original'] = keep_original
    args['primary'] = primary
    args['secondary'] = secondary

    _primary = validate_filepath(primary, allowed_file)

    if secondary:
        (_secondary_valid, _secondary_invalid) = validate_filepaths(secondary, allowed_file)

        for p in _secondary_invalid:
            click.echo(f"WARNING: Ignoring invalid file: {p}")

        if len(_secondary_valid) < 1:
            raise click.UsageError("ERROR: No valid files.")
        elif len(_secondary_valid) == 1:
            if _primary == _secondary_valid[0]:
                raise click.UsageError(f"ERROR: Primary file is {_primary}. No secondary files to link to.")

    Q = Query()

    try:
        primary_do = LavaDataObject.from_file(
            _primary,
            _primary.stem,
            id_col=options['id_col'],
            date_col=options['date_col'],
            id2_col=options['id2_col']
        )
    except DataObjectIDColKeyError:
        click.echo('\nWARNING: ID Column Header (-i, --id-col) not specified '
                   'and default of "InstrID" not found in your PRIMARY file.')
        click.echo(f'         Creating one for you called "{CliLinkResults.COL_HEADER_LINK_ID}"\n')

        primary_do = LavaDataObject.from_file(
            _primary,
            _primary.stem,
            id_col=None,
            date_col=options['date_col'],
            id2_col=options['id2_col']
        )
        primary_do.rename_id_col(CliLinkResults.COL_HEADER_LINK_ID)

    Q.add_node(
        primary_do,
        name=primary_do.name,
        operation=partial(group_by_keep_one,
                          group_by_col=primary_do.id2_col,
                          date_col=primary_do.date_col,
                          keep=options['primary_keep'],
                          id_col=primary_do.id_col,
                          drop_duplicates=False)
    )

    if secondary:
        for sec in _secondary_valid:
            try:
                secondary_do = LavaDataObject.from_file(
                    sec,
                    sec.stem,
                    id_col=options['secondary_id_col'],
                    date_col=options['secondary_date_col'],
                    id2_col=options['secondary_id2_col']
                )

                Q.add_node(secondary_do)

                Q.add_edge(
                    primary_do,
                    secondary_do,
                    name=secondary_do.name,
                    operation=partial(date_proximity,
                                      id_left_on=primary_do.id2_col,
                                      id_right_on=secondary_do.id2_col,
                                      date_left_on=primary_do.date_col,
                                      date_right_on=secondary_do.date_col,
                                      get=options['secondary_get'],
                                      when=options['secondary_when'],
                                      days=options['secondary_days'],
                                      left_link_id=primary_do.id_col)
                )

            except ParserError:
                click.echo(f"WARNING: Ignoring un-importable file: {sec}")

    click.echo("Executing query...")
    Q.execute()
    click.echo("Writing query results...")

    results = CliLinkResults(ctx)
    results.write(Q)

    click.echo(f'\nLook for results in: {results.results_file.resolve()}\n')

    if options['verbose']:
        print_ctx(ctx)
