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