from abc import ABC, abstractmethod
from collections import OrderedDict
import os

import requests
from typing import Dict, Iterable, List

from . import crate

HIPAACRATE_BUNDLES_ENDPOINT = "/bundles"
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


class FSBundleLoader(BundleLoader):
    def __init__(self, directory: str = HIPAACRATE_BUNDLES_PREFIX) -> None:
        self.directory = directory
    
    def load(self, name: str) -> crate.Crate:
        return crate.read_yaml(os.path.join(self.directory, name))

class HTTPBundleLoader(BundleLoader):
    def __init__(self, host: str, endpoint: str = HIPAACRATE_BUNDLES_ENDPOINT) -> None:
        if host.endswith("/"):
            host = host[:-1]
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        if not endpoint.startswith("/"):
            endpoint = "/{}".format(endpoint)
        
        self.host = host
        self.endpoint = endpoint
    
    def load(self, name: str) -> crate.Crate:
        r = requests.get("{}{}/{}".format(self.host, self.endpoint, name))
        r.raise_for_status()
        return crate.parse(r.text)

class CachingBundleLoader(BundleLoader):
    def __init__(self, host: str, endpoint: str = HIPAACRATE_BUNDLES_ENDPOINT,
                 cache_dir: str = HIPAACRATE_BUNDLES_PREFIX) -> None:
        self._http_loader = HTTPBundleLoader(host, endpoint)
        self._fs_loader = FSBundleLoader(cache_dir)
    
    @property
    def host(self) -> str:
        return self._http_loader.host
    
    @host.setter
    def host(self, value: str) -> None:
        self._http_loader.host = value
    
    @property
    def endpoint(self) -> str:
        return self._http_loader.endpoint
    
    @endpoint.setter
    def endpoint(self, value: str) -> None:
        self._http_loader.endpoint = value
    
    @property
    def cache_dir(self) -> str:
        return self._fs_loader.directory
    
    @cache_dir.setter
    def cache_dir(self, value: str) -> None:
        self._fs_loader.directory = value
    
    def load(self, name: str) -> crate.Crate:
        try:
            c = self._fs_loader.load(name)
        except FileNotFoundError:
            pass
        else:
            return c
        
        c = self._http_loader.load(name)
        c.to_yaml(os.path.join(self.cache_dir, c.name))

        return c