"""Implementation of :class:`ConfigurationBase` returning default configuration values
"""
from multiwindcalc import __name__ as DEFAULT_CATEGORY

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
