"""This module defines the generator parser
"""
import inspect
from ..specification import generator_methods
from ..util.validation import validate_type

class GeneratorsParser:
    def parse(self, generators):
        if generators is None:
            return {}
        validate_type(generators, dict, 'generators')

        generator_objects = {}
        for name, gen in generators.items():
            if 'method' not in gen:
                raise KeyError("Generator missing 'method'")
            method = gen['method']
            del gen['method']
            generator_objects[name] = self._instantiate(method, gen)
        return generator_objects

    @staticmethod
    def _instantiate(method, args):
        for name, _ in inspect.getmembers(generator_methods, inspect.isclass):
            if name == method:
                return getattr(generator_methods, name)(**args)
        raise KeyError("Method '" + method + "' not found in generator methods")
