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
"""Concrete implementation of :class:`SimulationInput` that writes JSON files"""
import json
import copy

from .simulation_input import SimulationInput


class JsonSimulationInputView(SimulationInput):
    """A dictionary input written as a JSON file where the parameter set is not deep-copied"""

    def __init__(self, parameter_set, **write_options):
        """Create a instance of :class:`JsonSimulationInput`

        :param parameter_set: Baseline parameter set
        :type parameter_set: dict
        """
        self._parameter_set = parameter_set
        self._write_options = write_options

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as fp:
            return cls(json.load(fp))

    def to_file(self, file_path):
        with open(file_path, 'w') as fw:
            json.dump(self._parameter_set, fw, **self._write_options)

    def hash(self):
        return hash(json.dumps(self._parameter_set))

    def __setitem__(self, key, value):
        self._parameter_set.__setitem__(key, value)

    def __getitem__(self, item):
        obj = self._parameter_set.__getitem__(item)
        if isinstance(obj, dict):
            return JsonSimulationInputView(obj, **self._write_options)
        return obj


class JsonSimulationInput(JsonSimulationInputView):
    """A dictionary input written as a JSON file where the parameter set is deep copied"""

    # pylint: disable=super-init-not-called
    def __init__(self, parameter_set, **write_options):
        """Create a instance of :class:`JsonSimulationInput`

        :param parameter_set: Baseline parameter set (deep copied)
        :type parameter_set: dict
        """
        self._parameter_set = copy.deepcopy(parameter_set)
        self._write_options = write_options
