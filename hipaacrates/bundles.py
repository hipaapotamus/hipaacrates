from abc import ABC, abstractmethod
from collections import OrderedDict
import os

from typing import Dict, Iterable, List

from . import crate

HIPAACRATE_BUNDLES_PREFIX = "hipaacrate_bundles"

class BundleLoader(ABC):
    @abstractmethod
    def load(self, name: str) -> crate.Crate:
        ...

def resolve_dependencies(crates: Iterable[crate.Crate]) -> List[crate.Crate]:
    resolved = []
    name_to_instance = dict((c.name, c) for c in crates)
    name_to_deps = dict((c.name, set([b.split(":")[0] for b in c.bundles])) for c in crates)

    while name_to_deps:
        ready = {name for name, deps in name_to_deps.items() if not deps}

        if not ready:
            raise ValueError("Circular dependencies found!")
        
        for name in ready:
            del name_to_deps[name]
        for deps in name_to_deps.values():
            deps.difference_update(ready)
        
        resolved.extend([name_to_instance[name] for name in sorted(ready)])
    
    return resolved

def load_dependencies(origin: crate.Crate, loader: BundleLoader) -> List[crate.Crate]:
    crates: Dict[str, crate.Crate] = OrderedDict()
    for dep in origin.bundles:
        dep_info = dep.split(":")
        c = loader.load(dep_info[0])
        crates[c.name] = c
        transitive_deps = load_dependencies(c, loader)
        for td in transitive_deps:
            crates[td.name] = td
    return list(crates.values())
