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
            value = configuration._get_value(category, key)
            if value is not None:
                return value
        return None
