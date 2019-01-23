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
"""Defines the base class for configuration implementations
"""
from abc import ABC, abstractmethod

DEFAULT_CATEGORY = 'spawn'

LIST_DELIMITER = ','

class ConfigurationBase(ABC):
    """Base class for configuration implementations.
    """

    default_category = DEFAULT_CATEGORY

    def get(self, category, key, parameter_type=str, default=None):
        """Gets the configuration value corresponding to the category and key.

        :param category: The category of the configuration parameter
        :type category: str
        :param key: The key of the configuration parameter
        :type key: str
        :param parameter_type: The type of the configuration parameter
        :type parameter_type: type
        :param default: The default value to return if the configuration parameter is not found
        :type default: obj

        :returns: The configuration value
        :rtype: obj
        """
        raw_value = self._get_value(category, key)
        if raw_value is None:
            return default
        if parameter_type == list:
            return raw_value.split(LIST_DELIMITER)
        try:
            return parameter_type(raw_value)
        except ValueError:
            raise ValueError((
                'Configuration parmaeter {} for key {}.{} ' +
                'could not be converted to type {}'
            ).format(raw_value, category, key, parameter_type))

    @abstractmethod
    def _get_value(self, category, key):
        raise NotImplementedError()
