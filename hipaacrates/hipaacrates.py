import hashlib
import os
import tempfile

from filelock import FileLock, Timeout
from typing import Any, Iterable

from . import bundles
from . import crate
from . import dockerfile
from . import services

HIPAACRATE_FILENAME = "Hipaacrate"

def hipaacrate_guard(method):
    def wrapper(self, *args, **kwargs):
        try:
            with self._lock:
                return method(self, *args, **kwargs)
        except Timeout as e:
            raise HipaacrateLockTimeout("failed to acquire hipaacrate lock file") from e
    
    return wrapper

class Hipaacrates(object):
    def __init__(self, bundle_repo: bundles.BundleRepository, filename: str = None) -> None:
        if filename is None:
            filename = HIPAACRATE_FILENAME
        self.bundle_repo = bundle_repo
        self.filename = filename
        self._lock = FileLock(_get_lock_file_name(), timeout=0.1)

    def _get_crate(self) -> crate.Crate:
        try:
            return crate.read_yaml(self.filename)
        except FileNotFoundError as e:
            raise HipaacrateFileError("could not open Hipaacrate file") from e
    
    def _save_crate(self, crate: crate.Crate) -> None:
        crate.to_yaml(self.filename)

    @hipaacrate_guard
    def init_file(self, name: str, version: str) -> None:
        c = crate.new(name, version)
        c.to_yaml(self.filename)
    
    @hipaacrate_guard
    def build_dockerfile(self):
        c = self._get_crate()
        # Load dependencies for the local Hipaacrate
        deps = bundles.load_dependencies(c, self.bundle_repo)
        # Make shell scripts for the necessary services
        scripts = services.make_scripts(deps)
        cmd = services.make_script(c)
        scripts[c.name] = cmd
        services.to_file(scripts)
        # Finally, make the Dockerfile
        dockerfile.make_file(c, deps)
    
    @hipaacrate_guard
    def add_bundles(self, *names: str):
        c = self._get_crate()
        combined = set(c.bundles) | set(names)
        c.bundles = list(combined)
        c.bundles.sort()
        self._save_crate(c)
    
    @hipaacrate_guard
    def remove_bundles(self, *names: str):
        c = self._get_crate()
        to_remove = set(names)
        existing = set(c.bundles)
        if not existing >= to_remove:
            raise ValueError("no bundles named {} added".format(", ".join(to_remove - existing)))
        else:
            c.bundles = list(existing - to_remove)
            c.bundles.sort()
            self._save_crate(c)

    @hipaacrate_guard
    def include_files(self, *names: str):
        c = self._get_crate()
        combined = set(c.includes) | set(names)
        c.includes = list(combined)
        c.includes.sort()
        self._save_crate(c)

    @hipaacrate_guard
    def omit_files(self, *names: str):
        c = self._get_crate()
        to_remove = set(names)
        existing = set(c.includes)
        if not existing >= to_remove:
            raise ValueError("no files named {} included".format(", ".join(to_remove - existing)))
        else:
            c.includes = list(existing - to_remove)
            c.includes.sort()
            self._save_crate(c)

    @hipaacrate_guard
    def get_value(self, key: str) -> Any:
        c = self._get_crate()
        return getattr(c, key)
    
    @hipaacrate_guard
    def set_value(self, key: str, value: Any) -> Any:
        c = self._get_crate()
        prev = getattr(c, key)
        setattr(c, key, value)
        return prev

class HipaacrateFileError(Exception):
    pass

class HipaacrateLockTimeout(Exception):
    pass

def _get_lock_file_name() -> str:
    return os.path.join(
        tempfile.gettempdir(),
        _hash_cwd(),
    )

def _hash_cwd() -> str:
    return hashlib.sha256(os.getcwdb()).hexdigest()