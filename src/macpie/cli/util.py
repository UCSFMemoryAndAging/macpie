import click

from macpie.io import has_csv_extension, has_excel_extension


def allowed_file(p):
    """Determines if a file is considered allowed
    """
    stem = p.stem
    if stem.startswith('~') or stem.startswith('results_'):
        return False
    if has_csv_extension(p) or has_excel_extension(p):
        return True
    return False


def iterate_params(params):
    results = []
    for k, v in params.items():
        if isinstance(v, tuple):
            for a in v:
                results.append((k, a))
        else:
            results.append((k, v))
    return results


def print_params(d):
    for k, v in d.items():
        if isinstance(v, tuple):
            click.echo(k + ':')
            for a in v:
                click.echo(f'\t{a}')
        else:
            click.echo(f'{k}: {v}')


def print_ctx(ctx):
    click.echo('COMMAND SUMMARY')
    click.echo('===============')
    click.echo(f'command: {ctx.info_name}')

    click.echo('\nOptions')
    click.echo('-------')
    print_params(ctx.obj['options'])

    click.echo('\nArguments')
    click.echo('---------')
    print_params(ctx.obj['args'])

    click.echo('\nSystem')
    click.echo('-------')
    print_params(ctx.obj['system'])

    click.echo()
