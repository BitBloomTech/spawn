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
"""Defines the plugin loader
"""
from importlib import import_module
from inspect import signature

from spawn.specification.generator_methods import Generator
from spawn.specification.evaluators import create_function_evaluator

def _load_plugin(plugin_definition):
    if not ':' in plugin_definition:
        raise ValueError(
            'plugin_definition {} does not have the expected format (plugin_type:plugin_path)'
            .format(plugin_definition)
        )
    plugin_type, module_path = plugin_definition.split(':')
    try:
        plugin = import_module(module_path)
    except ImportError:
        raise ValueError((
            'Could not import module {} for plugin definition {} - ' +
            'please make sure the module is available on your python path'
        ).format(module_path, plugin_definition))
    return (plugin_type, plugin)

RESERVED_NAMES = [
    'create_spawner'
]

class PluginLoader:
    """Class to load plugins and create spawners from plugins
    """

    _pre_loaded_plugins = {}

    def __init__(self, config):
        """Initialises the plugin spawner

        :param config: A configuration object
        :type config: :class:`ConfigurationBase`
        """
        self._config = config
        plugin_definitions = self._config.get(self._config.default_category, 'plugins', parameter_type=list, default=[])
        self._plugins = {**self._pre_loaded_plugins}
        for plugin_def in plugin_definitions:
            plugin_name, plugin = _load_plugin(plugin_def)
            self._plugins[plugin_name] = plugin

    @classmethod
    def pre_load_plugin(cls, name, plugin):
        """Pre-loads the specified plugin

        Adds the plugin to the pre-loaded plugins static map

        :param name: The name of the plugin
        :type name: str
        :param plugin: The plugin to load
        :type plugin: obj
        """
        cls._pre_loaded_plugins[name] = plugin

    def create_spawner(self, plugin_type):
        """Creates a spawner for a particular plugin type

        :param plugin_type: The type of plugin to create a spawner for
        :type plugin_type: str

        :returns: A spawner
        :rtype: :class:`TaskSpawner`
        """
        if not plugin_type in self._plugins:
            raise ValueError('Could not find plugin for plugin type {}'.format(plugin_type))
        plugin = self._plugins[plugin_type]
        if not hasattr(plugin, 'create_spawner'):
            raise TypeError('Plugin {} has no method create_spawner'.format(plugin_type))
        arg_names = signature(plugin.create_spawner).parameters
        arg_values = {
            n: self._config.get(plugin_type, n) or self._config.get(self._config.default_category, n)
            for n in arg_names
        }
        return plugin.create_spawner(**arg_values)

    def load_generators(self):
        """Loads generators from the plugins defined.

        Finds any classes of type :class:`Generator` in the plugin, and loads them

        :returns: dict of names and :class:`Generator`
        :rtype: dict
        """
        generators = {}
        for plugin in self._plugins.values():
            for name, value in plugin.__dict__.items():
                if name not in generators and self._is_generator(value):
                    generators[name] = value
        return generators

    def load_evaluators(self):
        """Loads evaluators from the plugins defined

        Finds any functions that are not prefixed with _, are not generators and are not reserved

        :returns: dict of names and :class:`Evaluator`
        :rtype: dict
        """
        evaluators = {}
        for plugin in self._plugins.values():
            for name, value in plugin.__dict__.items():
                if (name not in evaluators and
                        not self._is_generator(value) and
                        not self._is_ignored(name) and
                        self._is_evaluator(value)
                   ):
                    evaluators[name] = create_function_evaluator(value)
        return evaluators


    @staticmethod
    def _is_generator(value):
        return isinstance(value, type) and issubclass(value, Generator)

    @staticmethod
    def _is_evaluator(value):
        return callable(value)

    @staticmethod
    def _is_ignored(name):
        return name.startswith('_') or any(name == reserved_name for reserved_name in RESERVED_NAMES)
