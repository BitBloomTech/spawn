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
"""Spawner implementation that spawns :class:`SimulationTask`s taking a single input file path as its only command line
 argument"""
from os import path, makedirs
import copy

from ..tasks import SimulationTask
from ..simulation_inputs import SimulationInput
from .task_spawner import TaskSpawner


class SingleInputFileSpawner(TaskSpawner):
    """Runs bespoke executable taking a single input file as its only command line argument"""

    def __init__(self, simulation_input, file_name):
        """Create a instance of :class:`SingleInputFileSpawner`

        :param simulation_input: Simulation input file write
        :type simulation_input: :class:`SimulationInput`
        :param file_name: Name of input file for simulation, including extension but excluding path
        :type file_name: str
        """
        if not isinstance(simulation_input, SimulationInput):
            raise TypeError("simulation_input must be of type SimulationInput")
        self.__dict__['__simulation_input'] = simulation_input
        self.__dict__['__file_name'] = file_name

    def spawn(self, path_, metadata):
        if not path.isdir(path_):
            makedirs(path_)
        input_file_path = path.join(path_, self.__dict__['__file_name'])
        self.__dict__['__simulation_input'].to_file(input_file_path)
        return SimulationTask(_id=path_,
                              _input_file_path=input_file_path,
                              _metadata=metadata)

    def branch(self):
        return SingleInputFileSpawner(copy.deepcopy(self.__dict__['__simulation_input']), self.__dict__['__file_name'])

    def __getattr__(self, item):
        if item.startswith('__') and item.endswith('__'):
            # pylint: disable=no-member
            return super().__getattr__(item)
        return self.__dict__['__simulation_input'][item]

    def __setattr__(self, key, value):
        if key.startswith('__') and key.endswith('__'):
            super().__setattr__(key, value)
        else:
            self.__dict__['__simulation_input'][key] = value
