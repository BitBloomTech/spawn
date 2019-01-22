"""Defines the local implementation of :class:`SpawnInterface`
"""
import logging
from os import path
import json

from spawn import __name__ as APP_NAME
from spawn.plugins import PluginLoader
from spawn.parsers import SpecificationParser, DictSpecificationProvider
from spawn.specification import DictSpecificationConverter
from spawn.schedulers import LuigiScheduler

from .spawn import SpawnInterface

LOGGER = logging.getLogger(__name__)

class LocalInterface(SpawnInterface):
    """Defines the :class:`LocalInterface`

    A local implementation of the spawn interface
    """

    def __init__(self, config):
        self._config = config
        self._plugin_loader = PluginLoader(config)

    def inspect(self, spec_dict):
        """Inspect the object

        :param spec_dict: The specfile object
        :type spec_dict: dict

        :returns: An expanded inspection dict
        :rtype: dict
        """
        spec = self._spec_dict_to_spec(spec_dict)
        return self._spec_to_spec_dict(spec)

    def stats(self, spec_dict):
        """Calculate stats for the spec

        :param spec_dict: The specfile object
        :type spec_dict: dict

        :returns: An dict containing stats about the object
        :rtype: dict
        """
        spec = self._spec_dict_to_spec(spec_dict)
        return {
            'leaf_count': len(spec.root_node.leaves)
        }

    def run(self, spec_dict):
        """Run the spec object on the luigi scheduler

        :param spec_dict: The specfile object
        :type spec_dict: dict
        """
        spec = self._spec_dict_to_spec(spec_dict)
        plugin_type = self._config.get(APP_NAME, 'type') or spec.metadata.spec_type
        if not plugin_type:
            raise ValueError((
                'No plugin type defined - please specify the --type argument ' +
                'or add a type property in the spec file'
            ))
        spawner = self._plugin_loader.create_spawner(plugin_type)
        scheduler = LuigiScheduler(self._config)
        inspection_file = path.join(self._config.get(APP_NAME, 'outfile'), 'spawn.json')
        LOGGER.info('Writing inspection to %s', inspection_file)
        with open(inspection_file, 'w') as fp:
            json.dump(self._spec_to_spec_dict(spec), fp, indent=2)
        scheduler.run(spawner, spec)

    def _spec_dict_to_spec(self, spec_dict):
        reader = DictSpecificationProvider(spec_dict)
        return SpecificationParser(reader, self._plugin_loader).parse()

    def _spec_to_spec_dict(self, spec):
        return DictSpecificationConverter().convert(spec)
