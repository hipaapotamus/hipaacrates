"""
Copyright 2018 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import codecs
import os
import re
from setuptools import setup, find_packages

"""
git tag {VERSION}
git push --tags
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
"""

def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    else:
        return "UNKNOWN"

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION = find_version("hipaacrates", "version.py")

setup(
    name="hipaacrates",
    version=VERSION,
    author="Jordan Matelsky, Miller Wilt",
    author_email="jordan.matelsky@jhuapl.edu, miller.wilt@jhuapl.edu",
    description="",
    license="Apache 2.0",
    keywords="",
    url="https://github.com/aplbran/hipaacrates/tarball/" + VERSION,
    packages=find_packages(exclude=("tests",)),
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
        ],
    },
    classifiers=[
    ]
)
