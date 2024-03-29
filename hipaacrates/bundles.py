from abc import ABC, abstractmethod
from collections import OrderedDict
import os

import requests
from typing import Dict, Iterable, List
from typing_extensions import Protocol

from . import crate

HIPAACRATE_BUNDLES_ENDPOINT = "/bundles"
HIPAACRATE_BUNDLES_CACHE_DIR = "hipaacrate_bundles"

class BundleLoader(Protocol):
    def load(self, name: str) -> crate.Crate:
        ...

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

def resolve_dependencies(origin: crate.Crate, dependencies: Iterable[crate.Crate]) -> List[crate.Crate]:
    crates = list(dependencies) + [origin]

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

class BundleRepository(object):
    def __init__(self, host: str, endpoint: str = HIPAACRATE_BUNDLES_ENDPOINT,
                 cache_dir: str = HIPAACRATE_BUNDLES_CACHE_DIR) -> None:
        if host.endswith("/"):
            host = host[:-1]
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        if not endpoint.startswith("/"):
            endpoint = "/{}".format(endpoint)
        
        self._host = host
        self._endpoint = endpoint
        self.cache_dir = cache_dir
    
    @property
    def host(self) -> str:
        return self._host
    
    @host.setter
    def host(self, value: str) -> None:
        if value.endswith("/"):
            value = value[:-1]
        self._host = value
    
    @property
    def endpoint(self) -> str:
        return self._endpoint
    
    @endpoint.setter
    def endpoint(self, value: str) -> None:
        if value.endswith("/"):
            value = value[:-1]
        if not value.startswith("/"):
            value = "/{}".format(value)
        self._endpoint = value
    
    def download(self, name: str, save_to_disk: bool = False) -> crate.Crate:
        r = requests.get("{}{}/{}".format(self.host, self.endpoint, name))
        r.raise_for_status()
        c = crate.parse(r.text)
        if save_to_disk:
            os.makedirs(self.cache_dir, mode=0o755, exist_ok=True)
            c.to_yaml(os.path.join(self.cache_dir, c.name))
        
        return c
    
    def load(self, name: str) -> crate.Crate:
        return crate.read_yaml(os.path.join(self.cache_dir, name))
    
    def remove(self, name: str) -> None:
        os.remove(os.path.join(self.cache_dir, name))
