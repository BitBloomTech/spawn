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
        self._config = configparser.ConfigParser() if path.isfile(ini_file) else None
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
