"""Defines evaluators
"""
from abc import abstractmethod
import inspect

from multiwindcalc.specification import ValueProxy

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
        return arg.evaluate(**kwargs) if isinstance(arg, ValueProxy) else arg

    @abstractmethod
    def _evaluate(self, *args):
        raise NotImplementedError()

class RangeEvaluator(Evaluator):
    """Implementation of :class:`Evaluator` that returns a range from range_min up to and including range_max, in steps of range_step
    """
    def _evaluate(self, range_min, range_max, range_step):
        return list(range(range_min, range_max + range_step, range_step))

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
