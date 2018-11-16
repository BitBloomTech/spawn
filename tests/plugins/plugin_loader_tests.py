import pytest

from multiwindcalc.plugins.plugin_loader import PluginLoader
from multiwindcalc.config import CommandLineConfiguration

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
    mocker.patch('multiwindcalc.plugins.plugin_loader.import_module', load_module_mock)
    config = CommandLineConfiguration(d=('plugins=test_plugin:mock_plugin','test_plugin.foo=bar'))
    return PluginLoader(config)

def test_module_is_loaded(plugin_loader):
    assert True

def test_module_is_called_with_correct_arg(plugin_loader):
    assert plugin_loader.create_spawner('test_plugin') == 'bar'
