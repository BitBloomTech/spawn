import pytest

from multiwindcalc.config.composite import CompositeConfiguration
from multiwindcalc.config.command_line import CommandLineConfiguration, DEFAULT_CATEGORY

@pytest.fixture
def config():
    config_a = CommandLineConfiguration(foo='bar', baz='42')
    config_b = CommandLineConfiguration(foo='boo', far='8.3')
    return CompositeConfiguration(config_a, config_b)

def test_returns_first_if_present_in_both(config):
    assert config.get(DEFAULT_CATEGORY, 'foo') == 'bar'

def test_returns_first_if_only_present_in_first(config):
    assert config.get(DEFAULT_CATEGORY, 'baz', type=int) == 42

def test_returns_second_if_only_present_in_second(config):
    assert config.get(DEFAULT_CATEGORY, 'far', type=float) == 8.3

def test_returns_none_if_not_present_in_either(config):
    assert config.get(DEFAULT_CATEGORY, 'workers') is None

def test_returns_default_if_not_present_in_either(config):
    assert config.get(DEFAULT_CATEGORY, 'workers', type=int, default=4) == 4
