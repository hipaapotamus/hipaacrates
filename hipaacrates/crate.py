from typing import Iterable, List

import yaml

class Crate(object):
    def __init__(self, name: str, version: str, author: str, bundles: List[str]) -> None:
        self.author = author
        self.bundles = bundles
        self.name = name
        self.version = version

    def __str__(self) -> str:
        return "Crate(name={}, version={}, author={}, bundles={}".format(
            self.name, self.version, self.author, self.bundles,
        )

    def to_yaml(self, filepath: str = None) -> str:
        yaml_text = yaml.safe_dump(dict(
            name=self.name,
            author=self.author,
            version=self.version,
            bundles=self.bundles,
        ), default_flow_style=False)

        if filepath is not None:
            with open(filepath, "w") as f:
                f.write(yaml_text)
        
        return yaml_text

def new(name: str, version: str, author: str = None, bundles: Iterable[str] = None) -> Crate:
    """
    Create a new Crate
    """
    if author is None:
        author = ""
    if bundles is None:
        bundles = []
    else:
        bundles = list(bundles)
    return Crate(name=name, version=version, author=author, bundles=bundles)

def parse(text: str) -> Crate:
    """
    Parse and load a Crate from a YAML string
    """
    parsed = yaml.safe_load(text)
    return Crate(
        name=parsed["name"],
        version=parsed["version"],
        author=parsed.get("author"),
        bundles=parsed.get("bundles")
    )

def read_yaml(filepath: str) -> Crate:
    """
    Load a Crate from a YAML file
    """
    with open(filepath) as f:
        return parse(f.read())
