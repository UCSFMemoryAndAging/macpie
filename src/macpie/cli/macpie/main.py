import click

from macpie import __version__
from macpie._config import get_option

from macpie.cli.core import ResultsResource
from macpie.cli.env import get_load_dotenv, load_dotenv

COMMAND_NAME = "MACPIE"

if get_load_dotenv(command=COMMAND_NAME):
    load_dotenv(command=COMMAND_NAME)


@click.group(context_settings=dict(auto_envvar_prefix=COMMAND_NAME))
@click.option("-v", "--verbose", is_flag=True, help="Will print verbose messages.")
@click.option("-i", "--id-col", default=get_option("dataset.id_col_name"), help="ID Column Header")
@click.option(
    "-d", "--date-col", default=get_option("dataset.date_col_name"), help="Date Column Header"
)
@click.option(
    "-j", "--id2-col", default=get_option("dataset.id2_col_name"), help="ID2 Column Header"
)
@click.version_option(__version__)
@click.pass_context
def main(ctx, verbose, id_col, date_col, id2_col):
    ctx.obj = ctx.with_resource(ResultsResource(ctx=ctx, verbose=verbose))


from .envfile import envfile
from .keepone import keepone
from .link import link
from .masker import masker
from .merge import merge
from .replace import replace

main.add_command(envfile)
main.add_command(keepone)
main.add_command(link)
main.add_command(masker)
main.add_command(merge)
main.add_command(replace)
