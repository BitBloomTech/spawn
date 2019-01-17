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
"""Generator methods
"""
import random
from spawn.specification.value_proxy import ValueProxy


class Generator(ValueProxy):
    """Abstract base class for generators
    """
    def evaluate(self):
        """Evaluate this generator
        """
        return NotImplementedError()


class RandomInt(Generator):
    """Generator of pseudo-random integer values

    Uses :class:`random.Random` with the parameters provided
    """
    #pylint: disable=redefined-builtin
    def __init__(self, min=1, max=999, seed=1):
        """Initialises :class:`RandomInt`
        :param min: Minimum value of variate range (inclusive), default=1
        :param max: Maximum value of variate range (inclusive), default=999
        :param seed: Seed for random number generation, default=1
        """
        self._generator = random.Random()
        self._generator.seed(seed)
        self._min = min
        self._max = max

    def evaluate(self):
        """Evaluate this generator

        Generates a random int between ``min`` and ``max``, given the ``seed``
        """
        return self._generator.randint(self._min, self._max)


class IncrementalInt(Generator):
    """Generator of incremental integers
    """
    def __init__(self, start=1, step=1):
        """Initialises :class:`IncrementalInt`

        :param start: Integer value to start at (first generate call will produce this number)
        :param step: Increment between generate calls
        """
        self._next_number = start
        self._step = step

    def evaluate(self):
        """Evaluate this generator

        Adds ``step`` to the previously generated value
        """
        v = self._next_number
        self._next_number += self._step
        return v
