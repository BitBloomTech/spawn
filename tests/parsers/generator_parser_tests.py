import pytest
from multiwindcalc.parsers.generators import GeneratorsParser


def test_can_instantiate_simple_generator():
    gens = GeneratorsParser().parse({'Gen1': {'method': 'RandomInt'}})
    assert 'Gen1' in gens
    assert isinstance(gens['Gen1'].evaluate(), int)


def test_passes_args_correctly():
    gen_spec = {'Gen1': {
        'method': 'IncrementalInt',
        'start': 50,
        'step': 2
    }}
    gens = GeneratorsParser().parse(gen_spec)
    assert gens['Gen1'].evaluate() == 50
    assert gens['Gen1'].evaluate() == 52


def test_raises_key_error_when_method_not_present():
    with pytest.raises(KeyError):
        GeneratorsParser().parse({'Gen1': {'key': 'val'}})


def test_raises_key_error_when_method_not_class_in_generator_methods():
    with pytest.raises(KeyError):
        GeneratorsParser().parse({'Gen1': {'method': 'list'}})
