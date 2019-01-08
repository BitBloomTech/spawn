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
from spawn.specification.specification import *

def test_returns_normal_node_for_normal_name():
    node = SpecificationNodeFactory().create(None, 'alpha', 42, None, {})
    assert type(node) == SpecificationNode
    assert node.property_name == 'alpha'
    assert node.property_value == 42

def test_returns_indexed_node_for_index_pattern_name():
    node = SpecificationNodeFactory().create(None, 'alpha[1]', 42, None, {})
    assert type(node) == IndexedNode
    assert node.index == 1
    assert node.property_name == 'alpha'
    assert node.property_value == 42
