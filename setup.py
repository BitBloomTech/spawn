# spawn
# Copyright (C) 2018, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
from setuptools import setup, find_packages
from os import path

import versioneer

PACKAGE_NAME = 'spawn'

_here = path.abspath(path.dirname(__file__))

with open(path.join(_here, 'README.md')) as fp:
    README_CONTENTS = fp.read()

install_requires = [
    'luigi==2.8.2',
    'setuptools>=38.3',
    'click==7.0',
    'appdirs==1.4.3'
]

tests_require = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'pylint',
    'numpy',
    'pandas',
    'tox',
    'licensify'
]

extras_require = {
    'test': tests_require,
    'docs': ['sphinx', 'sphinx-click', 'm2r'],
    'publish': ['twine']
}

setup(
    name=PACKAGE_NAME,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    packages=find_packages(exclude=('tests*',)),
    cmdclass=versioneer.get_cmdclass(),
    license='GPLv3',
    version=versioneer.get_version(),
    author='Simmovation Ltd',
    author_email='info@simmovation.tech',
    url='https://github.com/Simmovation/spawn',
    platforms='any',
    description='Spawn is a python package that allows users to concisely specify and execute a large number of tasks with complex and co-dependent input parameter variations',
    long_description=README_CONTENTS,
    long_description_content_type='text/markdown',
    python_requires='>=3.6,<4',
    entry_points={
        'console_scripts': ['spawn=spawn.cli:cli'],
    },
)
