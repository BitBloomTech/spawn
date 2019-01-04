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

from spawn.util.path_builder import *

def test_convert_to_string_returns_empty_string_for_default_path_builder():
    assert str(PathBuilder()) == ''

def test_convert_to_string_returns_ctor_arg():
    assert str(PathBuilder('hello')) == 'hello'

def test_format_returns_ctor_arg():
    assert str(PathBuilder('hello').format({})) == 'hello'

def test_join_adds_to_end_of_path():
    assert str(PathBuilder('hello').join('world')) == 'hello/world'

def test_join_start_adds_to_start_of_path():
    assert str(PathBuilder('hello').join_start('world')) == 'world/hello'

def test_format_does_keyword_replacement():
    assert str(PathBuilder('{foo}').format(dict(foo='hello'))) == 'hello'

def test_format_does_multiple_keyword_replacement():
    assert str(PathBuilder('{foo}/{bar}').format(dict(foo='hello', bar='world'))) == 'hello/world'

@pytest.mark.parametrize('path,properties,indices,expected', [
    ('hello/{foo}', {'foo': 42.0}, {'foo': 4}, 'hello/42.0'),
    ('hello/{foo:1}', {'foo': 'world'}, {'foo': 4}, 'hello/5'),
    ('hello/{foo:0}/{bar:aa}', {'foo': 'world', 'bar': 42.0}, {'foo': 42, 'bar': 7}, 'hello/42/ah'),
])
def test_format_provides_correct_substitution(path, properties, indices, expected):
    assert str(PathBuilder(path).format(properties, indices)) == expected

@pytest.mark.parametrize('path,properties,indices', [
    ('hello/{foo}/{bar}', {'foo': 'world'}, {}),
    ('hello/{foo:0}/{bar:aa}', {'foo': 'world'}, {'foo': 42}),
])
def test_format_raises_error_when_all_props_not_found(path, properties, indices):
    with pytest.raises(ValueError):
        PathBuilder(path).format(properties, indices)

@pytest.mark.parametrize('index,index_format,expected', [
    (0, '0', '0'),
    (0, '1', '1'),
    (9, '0', '9'),
    (9, '1', '10'),
    (9, '01', '10'),
    (42, '1', '43'),
    (42, '01', '43'),
    (0, '01', '01'),
    (10, '000', '010'),
    (0, 'a', 'a'),
    (1, 'a', 'b'),
    (26, 'a', 'ba'),
    (27, 'a', 'bb'),
    (52, 'a', 'ca'),
    (0, 'aa', 'aa'),
    (1, 'aa', 'ab'),
    (25, 'aa', 'az'),
    (25, 'aa', 'az'),
    (675, 'aa', 'zz'),
    (676, 'aa', 'baa'),
])
def test_index_returns_correct_value_for_index(index, index_format, expected):
    assert PathBuilder.index(index, index_format) == expected