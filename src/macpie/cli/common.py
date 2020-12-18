from collections import OrderedDict
import json
import platform

import click
import openpyxl as pyxl

from macpie import core, io, util


def allowed_file(p):
    """Determines if a file is considered allowed
    """
    stem = p.stem
    if stem.startswith('~'):
        return False
    if io.has_csv_extension(p) or io.has_excel_extension(p):
        return True
    return False


def format_basic(filepath):
    wb = pyxl.load_workbook(filepath)
    for ws in wb.worksheets:
        if ws.title.startswith('_'):
            util.pyxl.ws_autoadjust_colwidth(ws)
    wb.save(filepath)


def iterate_params(params, jsonify: bool = False):
    results = []
    for k, v in params.items():
        if isinstance(v, tuple):
            for a in v:
                results.append((k, a))
        else:
            results.append((k, v))

    if jsonify:
        return [(r[0], json.dumps(r[1], cls=core.MACPieJSONEncoder)) for r in results]
    return results


def print_params(d):
    for k, v in d.items():
        if isinstance(v, tuple):
            click.echo(k + ':')
            for a in v:
                click.echo(f'\t{a}')
        else:
            click.echo(f'{k}: {v}')


def get_system_info():
    sys_info = OrderedDict()
    sys_info['python_version'] = platform.python_version()
    sys_info['platform'] = platform.platform()
    sys_info['computer_network_name'] = platform.node()
    sys_info['macpie_version'] = get_version()
    return sys_info


def get_version():
    from macpie import __version__
    return __version__


def print_ctx(ctx):
    click.echo('COMMAND SUMMARY')
    click.echo('===============')
    click.echo(f'command: {ctx.info_name}')

    click.echo('\nOptions')
    click.echo('-------')
    print_params(ctx.obj.opts)

    click.echo('\nArguments')
    click.echo('---------')
    print_params(ctx.obj.args)

    click.echo('\nSystem')
    click.echo('-------')
    print_params(get_system_info())

    click.echo()
