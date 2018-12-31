# spawn
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
import pytest

from spawn.plugins.plugin_loader import PluginLoader
from spawn.config import CommandLineConfiguration

@pytest.fixture
def test_module(mocker):
    module = mocker.Mock()
    def create_spawner(foo):
        return foo
    module.create_spawner = create_spawner
    return module

@pytest.fixture
def plugin_loader(mocker, test_module):
    load_module_mock = mocker.Mock()
    load_module_mock.return_value = test_module
    mocker.patch('spawn.plugins.plugin_loader.import_module', load_module_mock)
    config = CommandLineConfiguration(d=('plugins=test_plugin:mock_plugin','test_plugin.foo=bar'))
    return PluginLoader(config)

def test_module_is_loaded(plugin_loader):
    assert True

def test_module_is_called_with_correct_arg(plugin_loader):
    assert plugin_loader.create_spawner('test_plugin') == 'bar'
