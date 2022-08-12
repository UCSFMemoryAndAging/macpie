import click

from macpie.cli.env import create_envfile, overwrite_envfile_option


@click.command()
@overwrite_envfile_option
@click.pass_context
def envfile(ctx, overwrite):
    create_envfile(ctx, overwrite=overwrite)
