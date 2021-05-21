import click
import sys
from .core import Core
from .uploader import Uploader
from .downloader import Downloader
from . import constants
from .logger import get_logger


_global_options = [
    click.option("--url", "-u", type=str, required=True),
    click.option("--debug/--no-debug", default=False, help="enable debug logging"),
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


class Mash(object):
    pass


@click.group(invoke_without_command=True)
@click.option(
    "--version/--no-version", "-v", default=False, help="show version. (default: False)"
)
@click.option("--aws-profile", default=None, help="aws profile name")
@click.pass_context
def cli(ctx, version, aws_profile):
    ctx.obj = Mash()
    ctx.obj.aws_profile = aws_profile
    if version:
        print(constants.VERSION)
        sys.exit()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(help="list local files.")
@global_options
@click.option("--download/--no-download", "-d", default=False, help="download files")
@click.pass_context
def list_local(ctx, url, debug, download):
    s3local = Downloader(url=url, logger=get_logger(debug=debug))
    paths = s3local.list_local_path(download=download)
    for path in paths:
        print(path)


@cli.command(help="list local files.")
@global_options
@click.pass_context
def list(ctx, url, debug):
    s3local = Downloader(url=url, logger=get_logger(debug=debug))
    paths = s3local.list_download_path()
    for path in paths:
        print(path)


@cli.command(help="download file by s3.")
@global_options
@click.option("--skip-exist/--no-skip-exist", default=True, help="download files")
@click.pass_context
def download(ctx, url, debug, skip_exist):
    s3local = Downloader(url=url, logger=get_logger(debug=debug))
    s3local.download(skip_exist=skip_exist)


@cli.command(help="delete file by s3.")
@global_options
@click.pass_context
def delete(ctx, url, debug):
    s3local = Core(url=url, logger=get_logger(debug=debug))
    s3local.delete()


@cli.command(help="upload file to s3.")
@click.option("--source", "-s", type=str, required=True)
@global_options
@click.pass_context
def upload(ctx, source, url, debug):
    s3local = Uploader(url=url, logger=get_logger(debug=debug))
    s3local.upload(source_path=source)


def main():
    cli(obj={})
