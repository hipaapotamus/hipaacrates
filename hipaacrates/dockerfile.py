from io import StringIO

from .crate import Crate

DEFAULT_BASE_IMAGE = "phusion/baseimage:0.10.1"
WORKDIR_PREFIX = "/opt/services"

def make_file(crate: Crate) -> None:
    content = make(crate)
    with open("Dockerfile", "w") as f:
        f.write(content + "\n")

def make(crate: Crate) -> str:
    string = StringIO()
    string.write(
        make_header(crate) + "\n"
    )
    string.write(
        convert_build_steps(crate) + "\n"
    )
    string.write(
        include_files(crate) + "\n"
    )
    string.write(
        make_service_definition(crate) + "\n"
    )
    return string.getvalue()

def make_header(crate: Crate, baseimage: str = None) -> str:
    if baseimage is None:
        baseimage = DEFAULT_BASE_IMAGE

    string = StringIO()
    string.write("FROM {}\n".format(baseimage))
    if crate.author:
        string.write("LABEL maintainer \"{}\"\n".format(crate.author))
    string.write("LABEL version \"{}\"\n".format(crate.version))
    string.write("WORKDIR {}/{}".format(WORKDIR_PREFIX, crate.name))

    return string.getvalue()

def convert_build_steps(crate: Crate) -> str:
    steps = [make_run_statement(step) for step in crate.build_steps]
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
