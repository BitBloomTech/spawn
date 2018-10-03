import random


class RandomInt:
    def __init__(self, min=1, max=999, seed=1):
        """
        Generator of random integer values
        :param min: Minimum value of variate range (inclusive), default=1
        :param max: Maximum value of variate range (inclusive), default=999
        :param seed: Seed for random number generation, default=1
        """
        self._generator = random.Random()
        self._generator.seed(seed)
        self._min = min
        self._max = max

    def evaluate(self):
        return self._generator.randint(self._min, self._max)


class IncrementalInt:
    def __init__(self, start=1, step=1):
        """
        Generator of incremental integers
        :param start: Integer value to start at (first generate call will produce this number)
        :param step: Increment between generate calls
        """
        self._next_number = start
        self._step = step

    def evaluate(self):
        v = self._next_number
        self._next_number += self._step
        return v
