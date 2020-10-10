from functools import partial
from pathlib import Path
from typing import Any, Optional

import click

from macpie.classes import LavaDataObject
from macpie.classes import Query
from macpie.exceptions import FileImportError
from macpie.io import allowed_file, get_files_from_dir
from macpie.pandas import date_proximity, group_by_keep_one
from macpie.util import add_suffix


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


@click.group()
@click.option('-v', '--verbose',
              is_flag=True,
              help="Will print verbose messages.")
@click.option('-i', '--id-col',
              default=LavaDataObject.FIELD_ID_COL_VALUE_DEFAULT,
              help="ID Column Header")
@click.option('-d', '--date-col',
              default=LavaDataObject.FIELD_DATE_COL_VALUE_DEFAULT,
              help="Date Column Header")
@click.option('-j', '--id2-col',
              default=LavaDataObject.FIELD_ID2_COL_VALUE_DEFAULT,
              help="ID2 Column Header")
@click.pass_context
def main(ctx, verbose, id_col, date_col, id2_col):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['id_col'] = id_col
    ctx.obj['date_col'] = date_col
    ctx.obj['id2_col'] = id2_col


@main.command()
@click.option('-k', '--primary-keep',
              default='all',
              type=click.Choice(['all', 'first', 'latest'], case_sensitive=False))
@click.option('-g', '--secondary-get',
              default='all',
              type=click.Choice(['all', 'closest'], case_sensitive=False))
@click.option('-d', '--secondary-days',
              default=90)
@click.option('-w', '--secondary-when',
              default='earlier_or_later',
              type=click.Choice(['earlier', 'later', 'earlier_or_later'], case_sensitive=False))
@click.argument('primary',
                nargs=1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.argument('secondary',
                nargs=-1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.pass_context
def link(ctx, primary_keep, secondary_get, secondary_days, secondary_when, primary, secondary):
    ctx.obj['primary_keep'] = primary_keep
    ctx.obj['secondary_get'] = secondary_get
    ctx.obj['secondary_days'] = secondary_days
    ctx.obj['secondary_when'] = secondary_when

    _primary = _validate_filepath(primary)

    if secondary:
        (_secondary_valid, _secondary_invalid) = _validate_filepaths(secondary)

        if len(_secondary_valid) == 1:
            if _primary == _secondary_valid[0]:
                raise click.UsageError(f"Error: Primary file is {_primary}. No secondary files to link to.")

    Q = Query()

    primary_do = LavaDataObject.from_file(
        _primary,
        _primary.stem,
        id_col=ctx.obj['id_col'],
        date_col=ctx.obj['date_col'],
        id2_col=ctx.obj['id2_col'],
    )

    Q.add_node(
        primary_do,
        name=add_suffix(primary_do.name, "_anchor", 31),
        operation=partial(group_by_keep_one,
                          group_by_col=primary_do.id2_col,
                          date_col=primary_do.date_col,
                          keep=ctx.obj['primary_keep'],
                          drop_duplicates=False
                          )
    )

    if secondary:
        for sec in _secondary_valid:
            try:
                secondary_do = LavaDataObject.from_file(
                    sec,
                    sec.stem,
                    id_col=ctx.obj['id_col'],
                    date_col=ctx.obj['date_col'],
                    id2_col=ctx.obj['id2_col']
                )

                Q.add_node(secondary_do)

                Q.add_edge(
                    primary_do,
                    secondary_do,
                    name=add_suffix(secondary_do.name, "_linked", 31),
                    operation=partial(date_proximity,
                                      id_left_on=primary_do.id2_col,
                                      id_right_on=secondary_do.id2_col,
                                      date_left_on=primary_do.date_col,
                                      date_right_on=secondary_do.date_col,
                                      get=ctx.obj['secondary_get'],
                                      when=ctx.obj['secondary_when'],
                                      days=ctx.obj['secondary_days'],
                                      left_link_id=primary_do.id_col
                                      )
                )

            except FileImportError:
                click.echo(f"Warning: Ignoring un-importable file: {sec}")

    click.echo("Executing query...")
    Q.execute()
    click.echo("Writing query results...")
    output_filepath = Q.write_excel()
    click.echo(f'\nLook for results in: {output_filepath.resolve()}\n')

    if ctx.obj['verbose']:
        _print_ctx(ctx)


@main.command()
@click.option('-k', '--keep',
              default='all',
              type=click.Choice(['all', 'first', 'latest'], case_sensitive=False))
@click.argument('primary',
                nargs=-1,
                type=ClickPath(exists=True, file_okay=True, dir_okay=True))
@click.pass_context
def keepone(ctx, keep, primary):
    ctx.obj['primary_keep'] = keep

    _primary_valid, _primary_invalid = _validate_filepaths(primary)

    Q = Query()

    for prim in _primary_valid:
        primary_do = LavaDataObject.from_file(
            prim,
            prim.stem,
            id_col=ctx.obj['id_col'],
            date_col=ctx.obj['date_col'],
            id2_col=ctx.obj['id2_col']
        )

        Q.add_node(
            primary_do,
            operation=partial(group_by_keep_one,
                              group_by_col=primary_do.id2_col,
                              date_col=primary_do.date_col,
                              keep=ctx.obj['primary_keep'],
                              drop_duplicates=False
                              )
        )

    click.echo("Executing query...")
    Q.execute()
    click.echo("Writing query results...")
    output_filepath = Q.write_excel()
    click.echo(f'\nLook for results in: {output_filepath.resolve()}\n')

    if ctx.obj['verbose']:
        _print_ctx(ctx)


def _print_ctx(ctx):
    click.echo('COMMAND SUMMARY')
    click.echo('===============')
    click.echo(f'command: {ctx.info_name}')
    params = ctx.obj
    params.update(ctx.params)

    for k, v in params.items():
        if isinstance(v, tuple):
            click.echo(k + ':')
            for a in v:
                click.echo(f'\t{a}')
        else:
            click.echo(f'{k}: {v}')

    click.echo()


def _validate_filepath(p):
    if not p.exists():
        raise click.UsageError('Error: File does not exist.')
    if p.is_dir():
        raise click.UsageError('Error: File is not a file but a directory.')
    if not allowed_file(p):
        raise click.UsageError('Error: File extension is not allowed.')
    return p


def _validate_filepaths(ps):
    all_ps = []
    for p in ps:
        if p.is_dir():
            all_ps.extend(get_files_from_dir(p))
        else:
            all_ps.append(p)

    valid_ps = []
    invalid_ps = []
    for p in all_ps:
        if p in valid_ps:
            continue
        elif not allowed_file(p):
            invalid_ps.append(p)
        else:
            valid_ps.append(p)

    for p in invalid_ps:
        click.echo(f"Warning: Ignoring invalid file: {p}")

    if len(valid_ps) < 1:
        raise click.UsageError("Error: No valid files.")

    return (valid_ps, invalid_ps)
