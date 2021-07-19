#!/usr/bin/env python

import os
import shutil
import distutils.command.clean
from pathlib import Path

from setuptools import setup, find_namespace_packages
from pkg_resources import get_distribution, DistributionNotFound
import torch

from ml.shutil import run as sh
from ml import logging

cwd = Path(__file__).parent
pkg = sh('basename -s .git `git config --get remote.origin.url`').lower()
PKG = pkg.upper()

def write_version_py(path, major=None, minor=None, patch=None, suffix='', sha='Unknown'):
    if major is None or minor is None or patch is None:
        major, minor, patch = sh("git describe --abbrev=0 --tags")[1:].split('.')
        sha = sh("git rev-parse HEAD")
        logging.info(f"Build version {major}.{minor}.{patch}-{sha}")

    path = Path(path).resolve()
    pkg = path.name
    PKG = pkg.upper()
    version = f'{major}.{minor}.{patch}{suffix}'
    if os.getenv(f'{PKG}_BUILD_VERSION'):
        assert os.getenv(f'{PKG}_BUILD_NUMBER') is not None
        build_number = int(os.getenv(f'{PKG}_BUILD_NUMBER'))
        version = os.getenv(f'{PKG}_BUILD_VERSION')
        if build_number > 1:
            version += '.post' + str(build_number)
    elif sha != 'Unknown':
        version += '+' + sha[:7]

    import time
    content = f"""# GENERATED VERSION FILE
# TIME: {time.asctime()}
__version__ = {repr(version)}
git_version = {repr(sha)}
"""

    with open(path / 'version.py', 'w') as f:
        f.write(content)
    
    return version


def dist_info(pkgname):
    try:
        return get_distribution(pkgname)
    except DistributionNotFound:
        return None

# TODO
class Clean(distutils.command.clean.clean):
    def run(self):
        import glob
        import re
        with open('.gitignore', 'r') as f:
            ignores = f.read()
            pat = re.compile(r'^#( BEGIN NOT-CLEAN-FILES )?')
            for wildcard in filter(None, ignores.split('\n')):
                match = pat.match(wildcard)
                if match:
                    if match.group(1):
                        # Marker is found and stop reading .gitignore.
                        break
                    # Ignore lines which begin with '#'.
                else:
                    for filename in glob.glob(wildcard):
                        print(f"removing {filename} to clean")
                        try:
                            os.remove(filename)
                        except OSError:
                            shutil.rmtree(filename, ignore_errors=True)

        # It's an old-style class in Python 2.7...
        distutils.command.clean.clean.run(self)


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


if __name__ == '__main__':
    namespaces = ['ml']
    packages = find_namespace_packages(include=['ml.*'])
    version = write_version_py(pkg.replace('-', '/'))

    name = sh('basename -s .git `git config --get remote.origin.url`').upper()
    logging.info(f"Building ml.audio")
    setup(
        name=name,
        version=version,
        author='Deep Patel',
        url='https://github.com/necla-ml/ML-Audio',
        description=f"NECLA ML-Audio Library",
        long_description=readme(),
        keywords='machine learning, audio recognition, audio classification',
        license='BSD-3',
        classifiers=[
            'License :: OSI Approved :: BSD License',
            'Operating System :: macOS/Ubuntu 16.04+',
            'Development Status :: 1 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        namespace_packages=namespaces,
        packages=namespaces + packages,
        install_requires=['ml'],
        zip_safe=False)
