# multiwindcalc
# Copyright (C) 2018, Simmovation Ltd.
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

from multiwindcalc import __name__ as APP_NAME

def _load_plugin(plugin_definition):
    if not ':' in plugin_definition:
        raise ValueError('plugin_definition {} does not have the expected format (plugin_type:plugin_path)'.format(plugin_definition))
    plugin_type, module_path = plugin_definition.split(':')
    try:
        plugin = import_module(module_path)
    except ImportError:
        raise ValueError('Could not import module {} for plugin definition {} - please make sure the module is available on your python path'.format(module_path, plugin_definition))
    if not hasattr(plugin, 'create_spawner'):
        raise TypeError('Plugin {} has no method create_spawner'.format(plugin_definition))
    return (plugin_type, plugin)

class PluginLoader:
    """Class to load plugins and create spawners from plugins
    """
    def __init__(self, config):
        """Initialises the plugin spawner
        
        :param config: A configuration object
        :type config: :class:`ConfigurationBase`
        """
        self._config = config
        plugin_definitions = self._config.get(APP_NAME, 'plugins', type=list, default=[])
        self._plugins = {}
        for p in plugin_definitions:
            plugin_name, plugin = _load_plugin(p)
            self._plugins[plugin_name] = plugin
    
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
        arg_names = signature(plugin.create_spawner).parameters
        arg_values = {n: self._config.get(plugin_type, n) or self._config.get(APP_NAME, n) for n in arg_names}
        return plugin.create_spawner(**arg_values)
