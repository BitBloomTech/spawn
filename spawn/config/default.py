# spawn
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
"""Implementation of :class:`ConfigurationBase` returning default configuration values
"""
from spawn import __name__ as DEFAULT_CATEGORY

from .base import ConfigurationBase

DEFAULT_CONFIGURATION = {
    DEFAULT_CATEGORY: {
        'workers': 4,
        'config_file': DEFAULT_CATEGORY + '.ini',
        'runner_type': 'process',
        'prereq_outdir': 'prerequisites'
    },
    'server': {
        'port': 8082,
        'host': 'localhost'
    }
}

class DefaultConfiguration(ConfigurationBase):
    """Implemenation of :class:`ConfigurationBase` returning default configuration values
    """
    @property
    def categories(self):
        """The categories in this configuration

        :returns: The categories
        :rtype: list
        """
        return list(DEFAULT_CONFIGURATION.keys())
    
    def keys(self, category):
        """The keys for the specified category in this configuration
        
        :param category: The category to retrieve keys for
        :type category: str

        :returns: The keys in the specified category
        :rtype: list
        """
        return list(DEFAULT_CONFIGURATION.get(category, {}).keys())

    def _get_value(self, category, key):
        return DEFAULT_CONFIGURATION.get(category, {}).get(key)
