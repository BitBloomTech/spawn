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

from multiwindcalc.specification.combinators import *

def test_zip_properties_raises_error_for_non_dict():
    with pytest.raises(TypeError):
        zip_properties(42)

def test_zip_properties_raises_error_for_not_all_lists():
    with pytest.raises(ValueError):
        zip_properties({'a': [1, 2, 3], 'b': 4})

def test_zip_properties_raises_error_for_different_length_lists():
    with pytest.raises(ValueError):
        zip_properties({'a': [1, 2, 3], 'b': [4, 5]})

def test_zip_properties_produces_zip():
    assert zip_properties({'a': [1, 2], 'b': [4, 5]}) == [{'a': 1, 'b': 4}, {'a': 2, 'b': 5}]

def test_product_raises_error_for_non_dict():
    with pytest.raises(TypeError):
        product(5)

def test_product_produces_product_for_two_lists():
    assert product({'a': [1, 2], 'b': [3, 4]}) == [{'a': 1, 'b': [3, 4]}, {'a': 2, 'b': [3, 4]}]

def test_product_produces_product_for_list_and_value():
    assert product({'a': [1, 2], 'b': 3}) == [{'a': 1, 'b': 3}, {'a': 2, 'b': 3}]

def test_product_returns_empty_for_empty():
    assert product({}) == []

def test_product_returns_argument_for_single_item_as_first_value():
    assert product({'a': 1, 'b': [2, 3]}) == [{'a': 1, 'b': [2, 3]}]

def test_product_returns_list_of_values_for_single_arg():
    assert product({'a': [1, 2]}) == [{'a': 1}, {'a': 2}]