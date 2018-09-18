import click

from . import bundles
from . import crate
from . import dockerfile
from . import hipaacrates
from . import services
from . import version

@click.group()
@click.option("--hipaacrates-file", envvar="HIPAACRATES_FILE", metavar="FILE", default=hipaacrates.HIPAACRATE_FILENAME)
@click.option("--bundles-host", envvar="HIPAACRATES_BUNDLES_HOST", metavar="HOST", default="")
@click.version_option(version.__version__, prog_name="crater")
@click.pass_context
def crater(ctx, hipaacrates_file, bundles_host):
    repo = bundles.BundleRepository(bundles_host)
    ctx.obj = hipaacrates.Hipaacrates(repo, hipaacrates_file)

@crater.command()
@click.pass_context
def build(ctx):
    ctx.obj.build_dockerfile()

@crater.command()
@click.argument("bundles", nargs=-1, metavar="BUNDLE [BUNDLE]...")
@click.pass_context
def add(ctx, bundles):
    if not bundles:
        ctx.fail("Expected one or more Bundle name")
    ctx.obj.add_bundles(*bundles)

@crater.command()
@click.argument("files", nargs=-1, metavar="FILE [FILE]...")
@click.pass_context
def include(ctx, files):
    if not files:
        ctx.fail("Expected one or more files")
    ctx.obj.include_files(*files)


@crater.command()
@click.option("-n", "--name", prompt=True, help="Crate name", metavar="NAME")
@click.option("-v", "--version", prompt=True, help="Crate version", metavar="VERSION")
@click.pass_context
def init(ctx, name, version) -> None:
    ctx.obj.init_file(name, version)

@crater.command()
@click.argument("files", nargs=-1, metavar="FILE [FILE]...")
@click.pass_context
def omit(ctx, files):
    if not files:
        ctx.fail("Expected one or more files")
    ctx.obj.omit_files(*files)

@crater.command()
@click.argument("bundles", nargs=-1, metavar="BUNDLE [BUNDLE]...")
@click.pass_context
def remove(ctx, bundles):
    if not bundles:
        ctx.fail("Expected one or more Bundle name")
    ctx.obj.remove_bundles(*bundles)

@crater.command()
@click.argument("key", type=click.Choice(["author", "name", "run_command", "version"]))
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    ctx.obj.set_value(key, value)

@crater.command()
@click.argument("key", type=click.Choice(["author", "build_steps", "bundles", "includes", "name", "run_command", "version"]))
@click.pass_context
def show(ctx, key) -> None:
    v = ctx.obj.get_value(key)
    if isinstance(v, (list, tuple)):
        v = ["- " + str(e) for e in v]
        v = "\n".join(v)
        click.echo("{}:\n{}".format(key, v))
    else:
        click.echo("{}: {}".format(key, v))

if __name__ == '__main__':
    # arguments aren't needed due to Click.
    # pylint: disable=E1120
    crater()
