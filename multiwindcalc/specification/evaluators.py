# multiwindcalc
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
"""Defines evaluators
"""
from abc import abstractmethod
import inspect

import numpy as np

from multiwindcalc.specification import ValueProxy, evaluate

class Evaluator(ValueProxy):
    """Evaluator base class implementation of :class:`ValueProxy`

    Implements the :method:`evaluate` method of the parent class to expand any arguments
    """
    def __init__(self, *args):
        """Initialises the :class:`Evaluator`

        :param args: The arguments (may be evaluators)
        :type args: args
        """
        self._args = args
    
    def evaluate(self, **kwargs):
        """Evaluates the value proxy.

        Expands any arguments that are evaluators, and calls the :method:`_evaluate` implementation
        required by base class
        """
        args = [self._evaluate_arg(a, **kwargs) for a in self._args]
        parameters = inspect.signature(self._evaluate).parameters
        if 'kwargs' in parameters:
            return self._evaluate(*args, **kwargs)
        else:
            return self._evaluate(*args)
    
    def _evaluate_arg(self, arg, **kwargs):
        return evaluate(arg, **kwargs) if isinstance(arg, ValueProxy) else arg

    @abstractmethod
    def _evaluate(self, *args):
        raise NotImplementedError()

class RangeEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that returns a range from range_min up to and including range_max, in steps of range_step
    """
    def _evaluate(self, range_min, range_max, range_step):
        values = np.arange(range_min, range_max + range_step, range_step)
        values = values[values <= range_max]
        return [float(v) for v in values]

class MultiplyEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that multiplies two numbers
    """
    def _evaluate(self, left, right):
        return left * right
    
class DivideEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that divides the left by right
    """
    def _evaluate(self, left, right):
        return left / right
    
class AddEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that adds two numbers
    """
    def _evaluate(self, left, right):
        return left + right

class SubtractEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that subtracts right from left
    """
    def _evaluate(self, left, right):
        return left - right

class ParameterEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that returns the value of a parameter in the keyword arguments
    """
    def _evaluate(self, parameter_name, **kwargs):
        return kwargs[parameter_name]

class RepeatEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that repeats a value or evaluator ``count`` times
    """
    def _evaluate(self, value, count, **kwargs):
        count = super()._evaluate_arg(count, **kwargs)
        values = []
        for _ in range(count):
            values.append(super()._evaluate_arg(value, **kwargs))
        return values
    
    def _evaluate_arg(self, arg, **kwargs):
        return arg

def create_function_evaluator(function):
    class FunctionEvaluator(Evaluator):
        """Implementation of :class:`Evaluator` that evaluates a delegate function
        """
        def _evaluate(self, *args, **kwargs):
            parameters = inspect.signature(function).parameters
            if 'kwargs' not in parameters:
                kwargs = {k: v for k, v in kwargs.items() if k in parameters}
            return function(*args, **kwargs)

    return FunctionEvaluator
