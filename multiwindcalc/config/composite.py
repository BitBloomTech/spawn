"""Composite :class:`ConfigurationBase` that can take config values from multiple sources
"""
from .base import ConfigurationBase

class CompositeConfiguration(ConfigurationBase):
    """Composite :class:`ConfigurationBase` that can take config values from multiple sources
    """
    def __init__(self, *configurations):
        self._configurations = configurations
    
    def _get_value(self, category, key):
        for configuration in self._configurations:
            value = configuration._get_value(category, key)
            if value is not None:
                return value
        return None
