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
"""Composite :class:`ConfigurationBase` that can take config values from multiple sources
"""
from .base import ConfigurationBase

class CompositeConfiguration(ConfigurationBase):
    """Composite :class:`ConfigurationBase` that can take config values from multiple sources
    """
    def __init__(self, *configurations):
        self._configurations = configurations

    @property
    def categories(self):
        """The categories in this configuration

        :returns: The categories
        :rtype: list
        """
        value = {}
        for configuration in self._configurations:
            value = {*configuration.categories, *value}
        return list(sorted(value))

    def keys(self, category):
        """The keys for the specified category in this configuration

        :param category: The category to retrieve keys for
        :type category: str

        :returns: The keys in the specified category
        :rtype: list
        """
        value = {}
        for configuration in self._configurations:
            value = {*configuration.keys(category), *value}
        return list(sorted(value))

    def _get_value(self, category, key):
        for configuration in self._configurations:
            #pylint: disable=protected-access
            value = configuration._get_value(category, key)
            if value is not None:
                return value
        return None
