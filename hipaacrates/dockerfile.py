from io import StringIO

from typing import Iterable

from . import services
from .bundles import BundleLoader, load_dependencies, resolve_dependencies
from .crate import Crate

DEFAULT_BASE_IMAGE = "phusion/baseimage:0.10.1"
WORKDIR_PREFIX = "/opt/services"

def make_file(crate: Crate, dependencies: Iterable[Crate]) -> None:
    content = make(crate, dependencies)
    with open("Dockerfile", "w") as f:
        f.write(content + "\n")

def make(crate: Crate, dependencies: Iterable[Crate]) -> str:
    crates = resolve_dependencies(crate, dependencies)

    string = StringIO()
    string.write(make_header(crate) + "\n")
    for c in crates:
        string.write("# Hipaacrate bundle {}, version {}\n".format(c.name, c.version))
        string.write(change_workdir(c) + "\n")
        string.write(include_files(c) + "\n")
        string.write(convert_build_steps(c) + "\n")
        string.write(make_service_definition(c) + "\n")
    return string.getvalue()

def make_header(crate: Crate, baseimage: str = None) -> str:
    if baseimage is None:
        baseimage = DEFAULT_BASE_IMAGE

    string = StringIO()
    string.write("FROM {}\n".format(baseimage))
    if crate.author:
        string.write("LABEL maintainer \"{}\"\n".format(crate.author))
    string.write("LABEL version \"{}\"".format(crate.version))

    return string.getvalue()

def change_workdir(crate: Crate, prefix: str = None) -> str:
    if prefix is None:
        prefix = WORKDIR_PREFIX
    else:
        if prefix.endswith("/"):
            prefix = prefix[:-1]
    return "WORKDIR {}/{}".format(prefix, crate.name)

def convert_build_steps(crate: Crate) -> str:
    steps = [make_run_statement(step) for step in crate.build_steps if step]
    return "\n".join(steps)

def make_run_statement(cmd: str) -> str:
    return "RUN {}".format(cmd) if cmd else ""

def include_files(crate: Crate) -> str:
    if crate.includes:
        all_files = " ".join(crate.includes)
        return "COPY {} {}/{}/".format(all_files, WORKDIR_PREFIX, crate.name)
    else:
        return ""

def make_copy_statement(src: str, dest: str) -> str:
    return "COPY {} {}".format(src, dest)

def make_service_definition(crate: Crate) -> str:
    if crate.run_command:
        string = StringIO()
        string.write("COPY .hipaacrates/{}.sh /etc/service/{}/run\n".format(
            crate.name, crate.name,
        ))
        string.write("RUN chmod a+x /etc/service/{}/run".format(crate.name))
        return string.getvalue()
    else:
        return ""
