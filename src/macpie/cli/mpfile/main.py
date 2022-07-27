import click

from .compare import compare


@click.group()
@click.pass_context
def main(
    ctx,
):
    ctx.obj = {}


main.add_command(compare)
