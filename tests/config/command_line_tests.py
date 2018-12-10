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
import pytest

from multiwindcalc.config.command_line import CommandLineConfiguration, DEFAULT_CATEGORY

def test_returns_none_when_no_config_provided():
    assert CommandLineConfiguration().get(DEFAULT_CATEGORY, 'foo') is None

def test_returns_default_when_default_provided():
    assert CommandLineConfiguration().get(DEFAULT_CATEGORY, 'foo', default=42) == 42

def test_returns_string_when_defined():
    assert CommandLineConfiguration(foo='bar').get(DEFAULT_CATEGORY, 'foo') == 'bar'

def test_does_not_return_default_when_value_found():
    assert CommandLineConfiguration(foo='bar').get(DEFAULT_CATEGORY, 'foo', default='baz') == 'bar'

def test_returns_int_when_int_defined_as_string():
    assert CommandLineConfiguration(foo='42').get(DEFAULT_CATEGORY, 'foo', type=int) == 42

def test_returns_float_when_int_defined_as_string():
    assert CommandLineConfiguration(foo='42').get(DEFAULT_CATEGORY, 'foo', type=float) == 42.0

def test_returns_zero_when_default_is_zero():
    assert CommandLineConfiguration(foo='0').get(DEFAULT_CATEGORY, 'foo', type=int) == 0

def test_returns_correct_value_when_definition_used_with_default_cat():
    assert CommandLineConfiguration(d=('foo=bar',)).get(DEFAULT_CATEGORY, 'foo') == 'bar'

def test_returns_correct_value_when_definition_used():
    assert CommandLineConfiguration(d=(DEFAULT_CATEGORY + '.foo=bar',)).get(DEFAULT_CATEGORY, 'foo') == 'bar'

def test_returns_correct_value_when_definition_has_dot():
    assert CommandLineConfiguration(d=('foo.bar.baz=42',)).get('foo', 'bar.baz', type=int) == 42
