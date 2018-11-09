"""Generator methods
"""
import random
from multiwindcalc.specification.value_proxy import ValueProxy


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
