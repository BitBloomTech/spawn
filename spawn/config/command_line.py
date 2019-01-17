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
"""Defines the a :class:`ConfigurationBase` implementation that parses values from the command line
"""
from .base import ConfigurationBase

DEFAULT_CATEGORY = 'spawn'

class CommandLineConfiguration(ConfigurationBase):
    """Implementation of :class:`ConfugurationBase` that is able to parse
    configuration values from command line arguments
    """

    def __init__(self, **kwargs):
        """Initialises :class:`CommandLineConfiguration`

        :param kwargs: The kwargs passed on the command line
        :type kwargs: kwargs
        """
        self._args = {DEFAULT_CATEGORY: {}}
        for k, v in kwargs.items():
            if k == 'd':
                for defintion in v:
                    key, value = defintion.split('=')
                    category, key = key.split('.', 1) if '.' in key else (DEFAULT_CATEGORY, key)
                    self._args.setdefault(category, {})
                    self._args[category][key] = value
            else:
                self._args[DEFAULT_CATEGORY][k] = v
    @property
    def categories(self):
        """The categories in this configuration

        :returns: The categories
        :rtype: list
        """
        return list(self._args.keys())

    def keys(self, category):
        """The keys for the specified category in this configuration

        :param category: The category to retrieve keys for
        :type category: str

        :returns: The keys in the specified category
        :rtype: list
        """
        return list(self._args.get(category, {}).keys())

    def _get_value(self, category, key):
        return self._args.get(category, {}).get(key)
