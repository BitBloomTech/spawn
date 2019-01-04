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

from spawn.config.composite import CompositeConfiguration
from spawn.config.command_line import CommandLineConfiguration, DEFAULT_CATEGORY

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
