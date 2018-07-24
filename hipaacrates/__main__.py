import hashlib
import os
import tempfile

import click
from filelock import FileLock, Timeout

from . import crate
from . import version

def _get_lock_file_name() -> str:
    return os.path.join(
        tempfile.gettempdir(),
        _hash_cwd(),
    )

def _hash_cwd() -> str:
    return hashlib.sha256(os.getcwdb()).hexdigest()

CRATE_FILE = "Hipaacrate"
LOCK_FILE = FileLock(_get_lock_file_name(), timeout=0.1)

@click.group()
@click.version_option(version.__version__, prog_name="crater")
def crater():
    pass

@crater.command()
@click.argument("bundles", nargs=-1, metavar="BUNDLE [BUNDLE]...")
@click.pass_context
def add(ctx, bundles):
    if not bundles:
        ctx.fail("Expected one or more Bundle name")

    try:
        LOCK_FILE.acquire()
        c = crate.read_yaml(CRATE_FILE)
    except FileNotFoundError:
        ctx.fail("Could not open the Hipaacrate file - have you run 'crater init'?")
    except Timeout:
        ctx.fail("The Hipaacrate file is currently locked - a separate process must be using it")
    else:
        combined = set(c.bundles) | set(bundles)
        c.bundles = list(combined)
        c.bundles.sort()
        c.to_yaml(CRATE_FILE)
        LOCK_FILE.release()

@crater.command()
@click.option("-n", "--name", prompt=True, help="Crate name", metavar="NAME")
@click.option("-v", "--version", prompt=True, help="Crate version", metavar="VERSION")
@click.pass_context
def init(ctx, name, version) -> None:
    try:
        LOCK_FILE.acquire()
    except Timeout:
        ctx.fail("The Hipaacrate file is currently locked - a separate process must be using it")
    else:
        c = crate.new(name, version)
        c.to_yaml(CRATE_FILE)
        LOCK_FILE.release()

@crater.command()
@click.argument("bundles", nargs=-1, metavar="BUNDLE [BUNDLE]...")
@click.pass_context
def remove(ctx, bundles):
    if not bundles:
        ctx.fail("Expected one or more Bundle name")

    try:
        LOCK_FILE.acquire()
        c = crate.read_yaml(CRATE_FILE)
    except FileNotFoundError:
        ctx.fail("Could not open the Hipaacrate file - have you run 'crater init'?")
    except Timeout:
        ctx.fail("The Hipaacrate file is currently locked - a separate process must be using it")
    else:
        to_remove = set(bundles)
        existing = set(c.bundles)
        if not existing >= to_remove:
            ctx.fail("No Bundles named {} added".format(", ".join(to_remove - existing)))
        else:
            c.bundles = list(existing - to_remove)
            c.bundles.sort()
            c.to_yaml(CRATE_FILE)
            LOCK_FILE.release()

@crater.command()
@click.argument("value", type=click.Choice(["author", "bundles", "name", "version"]))
@click.pass_context
def show(ctx, value) -> None:
    try:
        LOCK_FILE.acquire()
        c = crate.read_yaml(CRATE_FILE)
    except FileNotFoundError:
        ctx.fail("Could not open the Hipaacrate file - have you run 'crater init'?")
    except Timeout:
        ctx.fail("The Hipaacrate file is currently locked - a separate process must be using it")
    else:
        click.echo(getattr(c, value))
        LOCK_FILE.release()

if __name__ == '__main__':
    crater()
