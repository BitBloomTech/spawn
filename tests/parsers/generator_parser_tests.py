import pytest
from multiwindcalc.parsers.generators import GeneratorsParser


def test_can_instantiate_simple_generator():
    gens = GeneratorsParser().parse([{'method': 'RandomInt'}])
    assert len(gens) == 1
    assert isinstance(gens[0].evaluate(), int)


def test_passes_args_correctly():
    gen_spec = [{
        'method': 'IncrementalInt',
        'start': 50,
        'step': 2
    }]
    gens = GeneratorsParser().parse(gen_spec)
    assert len(gens) == 1
    assert gens[0].evaluate() == 50
    assert gens[0].evaluate() == 52


def test_raises_key_error_when_method_not_present():
    with pytest.raises(KeyError):
        GeneratorsParser().parse([{'key': 'val'}])


def test_raises_key_error_when_method_not_class_in_generator_methods():
    with pytest.raises(KeyError):
        GeneratorsParser().parse([{'method': 'list'}])
