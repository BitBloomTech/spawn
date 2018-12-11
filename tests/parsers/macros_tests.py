import pytest

from multiwindcalc.parsers.macros import MacrosParser
from multiwindcalc.parsers.value_proxy import ValueProxyParser
from multiwindcalc.parsers.constants import MACRO

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