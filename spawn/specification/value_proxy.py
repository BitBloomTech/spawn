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
"""Defines the basic :class:`ValueProxy` classes and functions
"""
import inspect

from spawn.util.validation import validate_type

class ValueProxy:
    """Base value proxy class

    A value proxy is anything that can be `evaluate` d in place of a value
    """
    #pylint: disable=no-self-use
    def evaluate(self):
        """Evaluates the :class:`ValueProxy`

        Must be implemented in a derived class

        :returns: A value
        :rtype: object
        """
        return NotImplementedError()


class Macro(ValueProxy):
    """Implementation of :class:`ValueProxy` that can contain a value
    """
    def __init__(self, value):
        """Initialises :class:`Macro`

        :param value: The value to contain within the :class:`Macro`
        :type value: object
        """
        self._value = value

    def evaluate(self):
        """Evaluates the :class:`Macro` - returns the value

        :returns: The value contained within the :class:`Macro`
        :rtype: object
        """
        return self._value

def evaluate(value_proxy, *args, **kwargs):
    """Utility function to evaluate a :class:`ValueProxy`

    Determines whether `kwargs` needs to be provided

    :param value_proxy: The :class:`ValueProxy` to evaluate
    :type value_proxy: :class:`VaWlueProxy`
    """
    validate_type(value_proxy, ValueProxy, 'value_proxy')
    parameters = inspect.signature(value_proxy.evaluate).parameters
    if 'kwargs' in parameters:
        return value_proxy.evaluate(*args, **kwargs)
    return value_proxy.evaluate(*args)
