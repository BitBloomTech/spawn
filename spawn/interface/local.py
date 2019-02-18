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
"""Defines the local implementation of :class:`SpawnInterface`
"""
import logging
from os import path
import json

from spawn.plugins import PluginLoader
from spawn.parsers import SpecificationParser
from spawn.specification import DictSpecificationConverter
from spawn.schedulers import LuigiScheduler

from .spawn import SpawnInterface
from .config import spawn_config

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
        plugin_type = self._config.get(self._config.default_category, 'type') or spec.metadata.spec_type
        if not plugin_type:
            raise ValueError((
                'No plugin type defined - please specify the --type argument ' +
                'or add a type property in the spec file'
            ))
        spawner = self._plugin_loader.create_spawner(plugin_type)
        scheduler = LuigiScheduler(self._config)
        inspection_file = path.join(self._config.get(self._config.default_category, 'outdir'), 'spawn.json')
        LOGGER.info('Writing inspection to %s', inspection_file)
        with open(inspection_file, 'w') as fp:
            json.dump(self._spec_to_spec_dict(spec), fp, indent=2)
        scheduler.run(spawner, spec)

    def _spec_dict_to_spec(self, spec_dict):
        return SpecificationParser(self._plugin_loader).parse(spec_dict)

    @staticmethod
    def _spec_to_spec_dict(spec):
        return DictSpecificationConverter().convert(spec)

def run(spec_dict, config=None):
    """Run the spec_dict

    :param spec_dict: The spec dict
    :type spec_dict: dict
    :param config: The config
    :type config: dict or :class:`ConfigurationBase`
    """
    config = spawn_config(**config) if isinstance(config, dict) else spawn_config() if config is None else config

    LocalInterface(config).run(spec_dict)

def inspect(spec_dict, config=None):
    """Inspect the spec_dict

    :param spec_dict: The spec dict
    :type spec_dict: dict
    :param config: The config
    :type config: dict or :class:`ConfigurationBase`
    """
    config = spawn_config(**config) if isinstance(config, dict) else spawn_config() if config is None else config

    return LocalInterface(config).inspect(spec_dict)
