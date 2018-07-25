from typing import Iterable, List

import yaml

class Crate(object):
    def __init__(self, name: str, version: str, author: str, build_steps: List[str], bundles: List[str],
                 includes: List[str], run_command: str) -> None:
        self.author = author
        self.build_steps = build_steps
        self.bundles = bundles
        self.includes = includes
        self.name = name
        self.run_command = run_command
        self.version = version

    def __str__(self) -> str:
        return "Crate(name={}, version={}, author={}, bundles={}".format(
            self.name, self.version, self.author, self.bundles,
        )

    def to_yaml(self, filepath: str = None) -> str:
        yaml_text = yaml.safe_dump(dict(
            author=self.author,
            build_steps=self.build_steps,
            bundles=self.bundles,
            includes=self.includes,
            name=self.name,
            run_command=self.run_command,
            version=self.version,
        ), default_flow_style=False)

        if filepath is not None:
            with open(filepath, "w") as f:
                f.write(yaml_text)
        
        return yaml_text

def new(name: str, version: str, author: str = None, build_steps: Iterable[str] = None,
        bundles: Iterable[str] = None, includes: Iterable[str] = None, run_command: str = None) -> Crate:
    """
    Create a new Crate
    """
    if author is None:
        author = ""
    build_steps = list(build_steps) if build_steps is not None else []
    bundles = list(bundles) if bundles is not None else []
    includes = list(includes) if includes is not None else []
    if run_command is None:
        run_command = ""

    return Crate(name=name, version=version, author=author, build_steps=build_steps,
                 bundles=bundles, includes=includes, run_command=run_command)

def parse(text: str) -> Crate:
    """
    Parse and load a Crate from a YAML string
    """
    parsed = yaml.safe_load(text)
    return new(
        name=parsed["name"],
        version=parsed["version"],
        author=parsed.get("author"),
        build_steps=parsed.get("build_steps"),
        bundles=parsed.get("bundles"),
        includes=parsed.get("includes"),
        run_command=parsed.get("run_command"),
    )

def read_yaml(filepath: str) -> Crate:
    """
    Load a Crate from a YAML file
    """
    with open(filepath) as f:
        return parse(f.read())
