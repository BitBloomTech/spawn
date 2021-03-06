# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
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
"""
spawn root module
=================================================

.. :platform: Unix, Windows
   :synopsis: Concisely declare and run simulations with many parameter permutations.
.. moduleauthor:: Michael Tinning <michael.tinning@simmovation.tech>
.. moduleauthor:: Philip Bradstock <philip.bradstock@simmovation.tech>
"""
__copyright__ = 'Copyright (C) 2018, Simmovation Ltd.'
__author__ = 'Simmovation Ltd.'

from .plugins import json_input_file as json_plugin
from .plugins import PluginLoader
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Default `run` and `inspect` should be local
from .interface import run_local as run, inspect_local as inspect, stats_local as stats, write_inspection

# Load built-in plugins
PluginLoader.pre_load_plugin('json', json_plugin)
