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
from spawn.specification.value_proxy import Macro, ValueProxy

from .value_proxy import ValueProxyParser
from ..util.validation import validate_type
from .value_libraries import ValueLibraries

MAX_PASSES = 10

class MacrosParser:
    """Parser for the macros section of the spec file
    """
    def __init__(self, value_libraries, value_proxy_parser):
        """Initialise :class:`MacrosParser`

        :param value_libraries: The value libraries
        :type value_libraries: :class:`ValueLibraries`
        :param value_proxy_parser: The value proxy parser
        :type value_proxy_parser: :class:`ValueProxyParser`
        """
        validate_type(value_proxy_parser, ValueProxyParser, 'value_proxy_parser')
        validate_type(value_libraries, ValueLibraries, 'value_libraries')
        self._value_proxy_parser = value_proxy_parser
        self._value_libraries = value_libraries

    def parse(self, macros):
        """Parse the macros section of the spec file.

        :param macros: The macros dict.
        Keys are the names of the macros, values are a the values that a macro takes
        when used as a value in the spec.
        :type macros: dict

        :returns: An dict containing the values for the specified macros.
        :rtype: dict
        """
        if macros is None:
            return {}
        validate_type(macros, dict, 'macros')

        pass_number = 1

        while macros and pass_number < MAX_PASSES:
            pass_number += 1
            for name, value in list(macros.items()):
                if self._value_proxy_parser.is_value_proxy(value):
                    try:
                        value = self._value_proxy_parser.parse(value).evaluate()
                    except LookupError:
                        continue
                if isinstance(value, dict):
                    try:
                        value = self._parse_dict(value)
                    except LookupError:
                        continue
                self._add_macro(name, value)
                macros.pop(name)
        if macros:
            raise LookupError((
                'Failed to parse macros - the following macros ' +
                'could not be parsed after {} passes: {}'
            ).format(MAX_PASSES, macros))
        return self._value_libraries.macros

    def _add_macro(self, name, value):
        if not isinstance(value, ValueProxy):
            value = Macro(value)
        self._value_libraries.macros[name] = value

    def _parse_dict(self, value):
        for k, v in value.items():
            parsed_v = v
            if self._value_proxy_parser.is_value_proxy(parsed_v):
                parsed_v = self._value_proxy_parser.parse(v).evaluate()
            if isinstance(parsed_v, dict):
                parsed_v = self._parse_dict(v)
            value[k] = parsed_v
        return value
