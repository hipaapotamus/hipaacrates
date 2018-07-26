import os

from typing import Dict

from .crate import Crate

HIPAACRATES_WORK_DIR = ".hipaacrates"

def make_scripts(crate: Crate) -> Dict[str, str]:
    core_script = "#!/bin/sh\n\n{}".format(crate.run_command)
    return {crate.name: core_script}

def to_file(scripts: Dict[str, str]) -> None:
    os.makedirs(HIPAACRATES_WORK_DIR, mode=0o775, exist_ok=True)
    for name, content in scripts.items():
        with open(os.path.join(HIPAACRATES_WORK_DIR, "{}.sh".format(name)), "w") as f:
            f.write(content + "\n")
