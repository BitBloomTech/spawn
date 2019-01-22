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
"""Defines the base class for the spawn interface
"""
from abc import ABC, abstractmethod

class SpawnInterface(ABC):
    """Defines the abstract base class :class:`SpawnInterface`

    Sub-classes should provide implementations for `inspect` and `run`
    """
    @abstractmethod
    def inspect(self, spec_dict):
        """Inspect the object

        :param spec_dict: The specfile object
        :type spec_dict: dict

        :returns: An expanded inspection dict
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    def stats(self, spec_dict):
        """Calculate stats for the spec

        :param spec_dict: The specfile object
        :type spec_dict: dict

        :returns: An dict containing stats about the object
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    def run(self, spec_dict):
        """Run the object

        :param spec_dict: The specfile object
        :type spec_dict: dict
        """
        raise NotImplementedError()
