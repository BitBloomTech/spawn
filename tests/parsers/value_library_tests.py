from multiwindcalc.specification.generator_methods import IncrementalInt
from multiwindcalc.parsers.value_library import GeneratorLibrary


def test_generators_library_creates_ints():
    lib = GeneratorLibrary({'MyGen': IncrementalInt(4, 2)})
    assert lib.is_ref_to_this_library('@MyGen')
    assert lib.is_ref_to_this_library('gen:MyGen')
    i1 = lib.create_value('@MyGen')
    i2 = lib.create_value('gen:MyGen')
    assert i1 == 4
    assert i2 == 6


def test_generators_library_uses_multiple_generators():
    lib = GeneratorLibrary({'First': IncrementalInt(4, 2),
                            'Second': IncrementalInt(4, 2)})
    assert lib.create_value('@First') == 4
    assert lib.create_value('@Second') == 4
