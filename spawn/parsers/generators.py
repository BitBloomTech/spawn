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
"""This module defines the generator parser
"""
import inspect
from ..specification import generator_methods
from ..util.validation import validate_type

class GeneratorsParser:
    """Parser for the generators section of the spec file
    """
    def __init__(self, generators):
        self._generators = generators

    def parse(self, generators):
        """Parse the generators section of the spec file.

        :param generators: The generators dict.
        Keys are the names of the generators, values are a dict specifying the generator.
        :type generators: dict

        :returns: An expanding dict containing the values for the specified generators.
        :rtype: dict
        """
        if generators is None:
            return {}
        validate_type(generators, dict, 'generators')

        generator_objects = {}
        for name, gen in generators.items():
            if 'method' not in gen:
                raise KeyError("Generator '{}' missing 'method'".format(name))
            method = gen['method']
            del gen['method']
            generator_objects[name] = self._instantiate(method, gen)
        return generator_objects

    def _instantiate(self, method, args):
        if method in self._generators:
            return self._generators[method](**args)
        raise KeyError("Method '" + method + "' not found in generator methods")

    @staticmethod
    def load_generators_from_module(module):
        """Loads generators from the specified module

        :returns: The :class:`GeneratorsParser`
        :rtype: :class:`GeneratorsParser`
        """
        is_generator = lambda c: inspect.isclass(c) and issubclass(c, generator_methods.Generator)
        return {name: class_type for name, class_type in inspect.getmembers(module, is_generator)}

    @classmethod
    def default(cls):
        """Returns the default :class:`GeneratorsParser`, which
        loads generators from the `generator_methods` module

        :returns: The :class:`GeneratorsParser`
        :rtype: :class:`GeneratorsParser`
        """
        return cls(cls.load_generators_from_module(generator_methods))
