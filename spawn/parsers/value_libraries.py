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
"""Class to store the value libraries used around `spawn`
"""
from copy import deepcopy

class ValueLibraries:
    """Container class for value libraries (generators, macros & evaluators)
    """
    def __init__(self, generators=None, macros=None, evaluators=None):
        """Initialises :class:`ValueLibraries`

        :param generators: The generators library
        :type generators: dict
        :param macros: The macros library
        :type macros: dict
        :param evaluators: The evaluators library
        :type evaluators: dict
        """
        self._generators = generators or {}
        self._macros = macros or {}
        self._evaluators = evaluators or {}

    @property
    def generators(self):
        """Generators library
        """
        return self._generators

    @property
    def macros(self):
        """Macros library
        """
        return self._macros

    @property
    def evaluators(self):
        """Evaluators library
        """
        return self._evaluators

    def copy(self):
        """Copies the values library

        :returns: A copy of this object
        :rtype: :class:`ValueLibraries`
        """
        return ValueLibraries(deepcopy(self._generators), deepcopy(self._macros), deepcopy(self._evaluators))
