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
import os

import shutil

from sphinx.cmd.build import build_main as build

GENERATED_RSTS = [
    'spawn',
    'spawn.cli',
    'spawn.parsers',
    'spawn.runners',
    'spawn.schedulers',
    'spawn.simulation_inputs',
    'spawn.spawners',
    'spawn.specification',
    'spawn.tasks',
    'spawn.util'
]

def rst_contents(module):
    underline = '='*len(module)
    return f'{module}\n{underline}\n\n.. automodule:: {module}\n\t:members:\n\t:imported-members:\n'

def generate():
    docs_dir = os.path.join(os.getcwd(), 'docs')
    build_dir = os.path.join(docs_dir, '_build')
    api_docs_dir = os.path.join(docs_dir, 'api')
    if os.path.isdir(api_docs_dir):
        shutil.rmtree(api_docs_dir)
    os.mkdir(api_docs_dir)
    for file in GENERATED_RSTS:
        with open(os.path.join(api_docs_dir, file + '.rst'), 'w+') as fp:
            fp.write(rst_contents(file))
    build([docs_dir, build_dir])

if __name__ == '__main__':
    generate()