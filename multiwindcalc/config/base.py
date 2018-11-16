"""Defines the base class for configuration implementations
"""
from abc import abstractmethod

LIST_DELIMITER = ','

class ConfigurationBase:
    """Base class for configuration implementations.
    """
    def get(self, category, key, type=str, default=None):
        """Gets the configuration value corresponding to the category and key.

        :param category: The category of the configuration parameter
        :type category: str
        :param key: The key of the configuration parameter
        :type key: str
        :param type: The type of the configuration parameter
        :type type: type
        :param default: The default value to return if the configuration parameter is not found
        :type default: obj

        :returns: The configuration value
        :rtype: obj
        """
        raw_value = self._get_value(category, key)
        if raw_value is None:
            return default
        if type == list:
            return raw_value.split(LIST_DELIMITER)
        try:
            return type(raw_value)
        except ValueError:
            raise ValueError('Configuration parmaeter {} for key {}.{} could not be converted to type {}'.format(raw_value, category, key, type))
    
    @abstractmethod
    def _get_value(self, category, key):
        raise NotImplementedError()
