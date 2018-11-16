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
    
    def _get_value(self, category, key):
        if self._config is not None and self._config.has_option(category, key):
            return self._config.get(category, key)
        return None
