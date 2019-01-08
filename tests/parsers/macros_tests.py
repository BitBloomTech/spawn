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

from spawn.parsers.macros import MacrosParser
from spawn.parsers.value_proxy import ValueProxyParser
from spawn.parsers.constants import MACRO

@pytest.fixture
def parser():
    value_libraries = {MACRO: {}}
    return MacrosParser(value_libraries, ValueProxyParser(value_libraries))

def test_can_parse_simple_macro(parser):
    result = parser.parse({'ref': 10})
    assert result['ref'].evaluate() == 10

def test_can_parse_referenced_macro(parser):
    result = parser.parse({'foo': 10, 'bar': '$foo'})
    assert result['foo'].evaluate() == 10
    assert result['bar'].evaluate() == 10

def test_can_parse_dict_macro(parser):
    result = parser.parse({'foo': 10, 'bar': {'baz': '$foo'}})
    assert result['foo'].evaluate() == 10
    assert result['bar'].evaluate() == {'baz': 10}