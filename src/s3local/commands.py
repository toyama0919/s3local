import click
import sys
from .core import Core
from . import constants


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False, help="enable debug logging")
@click.option(
    "--version/--no-version", "-v", default=False, help="show version. (default: False)"
)
@click.pass_context
def cli(ctx, debug, version):
    ctx.obj = Mash()
    if version:
        print(constants.VERSION)
        sys.exit()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(help="list local files.")
@click.option("--url", "-u", type=str, required=True)
@click.option("--download/--no-download", "-d", default=False, help="download files")
@click.pass_context
def list_local(ctx, url, download):
    s3local = Core(url=url)
    paths = s3local.list_local_path(download=download)
    for path in paths:
        print(path)


@cli.command(help="download file by s3.")
@click.option("--url", "-u", type=str, required=True)
@click.option("--skip-exist/--no-skip-exist", default=True, help="download files")
@click.pass_context
def download(ctx, url, skip_exist):
    s3local = Core(url=url)
    s3local.download(skip_exist=skip_exist)


@cli.command(help="delete file by s3.")
@click.option("--url", "-u", type=str, required=True)
@click.pass_context
def delete(ctx, url):
    s3local = Core(url=url)
    s3local.delete()


def main():
    cli(obj={})
