"""Implementation of :class:`ConfigurationBase` returning default configuration values
"""
from multiwindcalc import __name__ as DEFAULT_CATEGORY

from .base import ConfigurationBase

DEFAULT_CONFIGURATION = {
    DEFAULT_CATEGORY: {
        'workers': 4,
        'config_file': DEFAULT_CATEGORY + '.ini',
        'runner_type': 'process'
    },
    'server': {
        'port': 8082
    }
}

class DefaultConfiguration(ConfigurationBase):
    """Implemenation of :class:`ConfigurationBase` returning default configuration values
    """
    def _get_value(self, category, key):
        return DEFAULT_CONFIGURATION.get(category, {}).get(key)
