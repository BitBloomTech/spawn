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
"""Implementation of :class:`ConfigurationBase` that reads configuration from an ini file
"""
from os import path
import configparser

from .base import ConfigurationBase

class IniFileConfiguration(ConfigurationBase):
    """Implementation of :class:`ConfigurationBase` that reads configuration from an ini file
    """
    def __init__(self, ini_file):
        """Initialises :class:`ConfigurationBase`

        :param ini_file: The file to read
        :type ini_file: path-like
        """
        self._config = configparser.ConfigParser() if ini_file and path.isfile(ini_file) else None
        if self._config:
            self._config.read(ini_file)

    @property
    def categories(self):
        """The categories in this configuration

        :returns: The categories
        :rtype: list
        """
        return list(self._config.sections())

    def keys(self, category):
        """The keys for the specified category in this configuration

        :param category: The category to retrieve keys for
        :type category: str

        :returns: The keys in the specified category
        :rtype: list
        """
        return [] if not self._config.has_section(category) else list(self._config.options(category))

    def _get_value(self, category, key):
        if self._config is not None and self._config.has_option(category, key):
            return self._config.get(category, key)
        return None
