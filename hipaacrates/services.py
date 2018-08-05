import os

from typing import Dict, Iterable, Optional

from .crate import Crate

HIPAACRATES_WORK_DIR = ".hipaacrates"

def make_scripts(crates: Iterable[Crate]) -> Dict[str, str]:
    return {crate.name: make_script(crate) for crate in crates if crate.run_command}

def make_script(crate: Crate) -> str:
    if crate.run_command:
        return "#!/bin/sh\n\n{}".format(crate.run_command)
    return ""

def to_file(scripts: Dict[str, str]) -> None:
    os.makedirs(HIPAACRATES_WORK_DIR, mode=0o775, exist_ok=True)
    for name, content in scripts.items():
        with open(os.path.join(HIPAACRATES_WORK_DIR, "{}.sh".format(name)), "w") as f:
            f.write(content + "\n")
