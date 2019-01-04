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

from multiwindcalc.parsers.value_proxy import *
from multiwindcalc.specification.evaluators import *
from multiwindcalc.specification.value_proxy import *
from multiwindcalc.specification.generator_methods import *
from multiwindcalc.parsers.constants import EVALUATOR, GENERATOR, MACRO

@pytest.fixture
def parser():
    evaluator_library = {
        'range': RangeEvaluator,
        'repeat': RepeatEvaluator,
        'mult': MultiplyEvaluator,
        'div': DivideEvaluator,
        'add': AddEvaluator,
        'sub': SubtractEvaluator
    }
    macro_library = {
        'VRef': Macro(5)
    }
    generator_library = {
        'seed': IncrementalInt()
    }
    libraries = {
        EVALUATOR: evaluator_library,
        MACRO: macro_library,
        GENERATOR: generator_library
    }
    return ValueProxyParser(libraries)

def test_parser_returns_evaluator_for_valid_string(parser):
    assert isinstance(parser.parse('#range(1, 10, 1)'), RangeEvaluator)

def test_parser_returns_evaluator_with_correct_result(parser):
    assert parser.parse('#range(1, 5, 1)').evaluate() == list(range(1, 6, 1))

def test_parser_returns_correct_result_containing_multiply(parser):
    assert parser.parse('#range(1, 2 * 2, 1)').evaluate() == list(range(1, 5, 1))

def test_parser_returns_correct_result_containing_macros(parser):
    assert parser.parse('#range(1, $VRef, 1)').evaluate() == list(range(1, 6, 1))

def test_evaluation_of_parameters(parser):
    assert parser.parse('!value').evaluate(value=42) == 42

def test_evaluation_of_parameters_as_argumnts(parser):
    assert parser.parse('#range(1, !upper, !step)').evaluate(upper=4, step=1) == list(range(1, 5, 1))

def test_evaluation_of_negative_values(parser):
    assert parser.parse('#range(-180, 165, 15)').evaluate() == list(range(-180, 180, 15))

def test_evaluation_of_generator(parser):
    evaluator = parser.parse('@seed')
    assert evaluator.evaluate() == 1
    assert evaluator.evaluate() == 2

def test_evaluation_of_generator_as_argument(parser):
    evaluator = parser.parse('#range(1, @seed, 1)')
    assert evaluator.evaluate() == [1]
    assert evaluator.evaluate() == [1, 2]

def test_repeat_generator(parser):
    evaluator = parser.parse('#repeat(@seed, 3)')
    assert evaluator.evaluate() == [1, 2, 3]

def test_macro(parser):
    assert parser.parse('$VRef').evaluate() == 5

def test_basic_maths(parser):
    assert parser.parse('#2 * 2').evaluate() == 4

@pytest.mark.parametrize('value', [
    '#range(1, 10, 1)',
    'eval:range(1, 10, 1)',
    '#5 * 5',
    'eval:5 * 5',
    '!value',
    'param:value',
    '@seed',
    'gen:seed',
    '$VRef',
    'macro:VRef'
])
def test_is_value_proxy_returns_true_for_strings_starting_with_short_or_long_form(parser, value):
    assert parser.is_value_proxy(value)

@pytest.mark.parametrize('value', [
    'range(1, 10, 1)',
    'evl:range(1, 10, 1)',
    '5 * 5',
    'evl:5 * 5',
    'value',
    'pram:value',
    '?seed',
    'generator:seed',
    'VRef',
    'mcro:VRef'
])
def test_is_value_proxy_returns_false_for_strings_not_starting_with_short_or_long_form(parser, value):
    assert not parser.is_value_proxy(value)
