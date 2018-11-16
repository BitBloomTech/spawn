import pytest

from multiwindcalc.parsers.evaluators import *
from multiwindcalc.specification.evaluators import *
from multiwindcalc.specification.value_proxy import *
from multiwindcalc.specification.generator_methods import *

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
    return EvaluatorParser(evaluator_library, macro_library, generator_library)

def test_parser_returns_evaluator_for_valid_string(parser):
    assert isinstance(parser.parse('range(1, 10, 1)'), RangeEvaluator)

def test_parser_returns_evaluator_with_correct_result(parser):
    assert parser.parse('range(1, 5, 1)').evaluate() == list(range(1, 6, 1))

def test_parser_returns_correct_result_containing_multiply(parser):
    assert parser.parse('range(1, 2 * 2, 1)').evaluate() == list(range(1, 5, 1))

def test_parser_returns_correct_result_containing_macros(parser):
    assert parser.parse('range(1, $VRef, 1)').evaluate() == list(range(1, 6, 1))

def test_evaluation_of_parameters(parser):
    assert parser.parse('value').evaluate(value=42) == 42

def test_evaluation_of_parameters_as_argumnts(parser):
    assert parser.parse('range(1, upper, step)').evaluate(upper=4, step=1) == list(range(1, 5, 1))

def test_evaluation_of_generator(parser):
    evaluator = parser.parse('@seed')
    assert evaluator.evaluate() == 1
    assert evaluator.evaluate() == 2

def test_evaluation_of_generator_as_argument(parser):
    evaluator = parser.parse('range(1, @seed, 1)')
    assert evaluator.evaluate() == [1]
    assert evaluator.evaluate() == [1, 2]

def test_repeat_generator(parser):
    evaluator = parser.parse('repeat(@seed, 3)')
    assert evaluator.evaluate() == [1, 2, 3]

def test_macro(parser):
    assert parser.parse('$VRef').evaluate() == 5

def test_basic_maths(parser):
    assert parser.parse('2 * 2').evaluate() == 4