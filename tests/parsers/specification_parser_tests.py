import pytest

from multiwindcalc.specification.generator_methods import *
from multiwindcalc.specification.combinators import *
from multiwindcalc.parsers.specification_parser import *
from multiwindcalc.specification.specification import *

class DefaultSpecificationNodeParser(SpecificationNodeParser):
    def __init__(self, **kwargs):
        super().__init__(combinators={'zip': zip_properties, 'product': product}, default_combinator='product', **kwargs)

def test_parse_null_node_returns_root_node_no_children():
    node = DefaultSpecificationNodeParser().parse(None)
    assert node.is_root
    assert node.children == []

def test_parse_single_value_returns_correct_tree():
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': 8.0})
    assert root_node.is_root
    assert len(root_node.children) == 1
    node = root_node.children[0]
    assert node.property_name == 'wind_speed'
    assert node.property_value == 8.0
    assert node.children == []

def test_parse_multiple_values_returns_root_with_multiple_children():
    values = [8.0, 10.0, 12.0]
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': values})
    assert root_node.is_root
    assert len(root_node.children) == 3
    for i, expected_value in enumerate(values):
        node = root_node.children[i]
        assert node.property_name == 'wind_speed'
        assert node.property_value == expected_value
        assert node.children == []

def test_parse_multiple_properties_returns_multiple_levels():
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': 8.0, 'turbulence_intensity': '10%'})
    assert len(root_node.children) == 1
    assert root_node.children[0].property_name == 'wind_speed'
    assert root_node.children[0].property_value == 8.0
    assert len(root_node.children[0].children) == 1
    assert root_node.children[0].children[0].property_name == 'turbulence_intensity'
    assert root_node.children[0].children[0].property_value == '10%'

def test_parse_multiple_properties_returns_correct_leaf_nodes():
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': [8.0, 12.0], 'turbulence_intensity': ['10%', '20%']})
    print(root_node.children)
    assert len(root_node.leaves) == 4
    expected_args = [
        {'wind_speed': 8.0, 'turbulence_intensity': '10%'},
        {'wind_speed': 12.0, 'turbulence_intensity': '10%'},
        {'wind_speed': 8.0, 'turbulence_intensity': '20%'},
        {'wind_speed': 12.0, 'turbulence_intensity': '20%'},
    ]
    for leaf in root_node.leaves:
        expected_args.remove(leaf.collected_properties)
    assert expected_args == []

def test_parse_child_nodes_produces_correct_combinations():
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': 8.0, 'direction_0': {'wind_direction': 0.0, 'turbulence_intensity': '10%'}, 'direction_1': {'wind_direction': 180.0, 'turbulence_intensity': '20%'}})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0, 'turbulence_intensity': '10%'},
        {'wind_speed': 8.0, 'wind_direction': 180.0, 'turbulence_intensity': '20%'}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    for expected in expected_args:
        assert expected in collected_properties

def test_parse_child_node_list_produces_correct_combinations():
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': 8.0, 'directions': [{'wind_direction': 0.0, 'turbulence_intensity': '10%'}, {'wind_direction': 180.0, 'turbulence_intensity': '20%'}]})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0, 'turbulence_intensity': '10%'},
        {'wind_speed': 8.0, 'wind_direction': 180.0, 'turbulence_intensity': '20%'}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    for expected in expected_args:
        assert expected in collected_properties

def test_parse_with_zip_function_produces_pairs():
    root_node = DefaultSpecificationNodeParser().parse({'combine:zip': {'wind_speed': [8.0, 10.0], 'wind_direction': [0.0, 180.0]}})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0},
        {'wind_speed': 10.0, 'wind_direction': 180.0}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert expected_args == collected_properties

def test_parse_with_product_function_produces_pairs():
    root_node = DefaultSpecificationNodeParser().parse({'combine:product': {'wind_speed': [8.0, 10.0], 'wind_direction': [0.0, 180.0]}})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0},
        {'wind_speed': 8.0, 'wind_direction': 180.0},
        {'wind_speed': 10.0, 'wind_direction': 0.0},
        {'wind_speed': 10.0, 'wind_direction': 180.0}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert expected_args == collected_properties

def test_parse_with_implicit_product_and_zip_produces_expected_output():
    root_node = DefaultSpecificationNodeParser().parse({'wind_speed': [8.0, 10.0], 'combine:zip': { 'wind_direction': [0.0, 180.0], 'turbulence_intensity': ['0%', '20%']}})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0, 'turbulence_intensity': '0%'},
        {'wind_speed': 8.0, 'wind_direction': 180.0, 'turbulence_intensity': '20%'},
        {'wind_speed': 10.0, 'wind_direction': 0.0, 'turbulence_intensity': '0%'},
        {'wind_speed': 10.0, 'wind_direction': 180.0, 'turbulence_intensity': '20%'},
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert expected_args == collected_properties

def test_zip_function_raises_error_if_lists_have_unequal_size():
    with pytest.raises(ValueError):
        DefaultSpecificationNodeParser().parse({'combine:zip': {'wind_speed': [8.0, 10.0, 12.0], 'wind_direction': [0.0, 180.0]}})

@pytest.fixture(scope='function')
def parser_with_incremental_int_generator():
    generator_library = {
        'MyGen': IncrementalInt(4, 2)
    }
    return DefaultSpecificationNodeParser(value_libraries={'gen': generator_library})


def test_can_use_generator_once(parser_with_incremental_int_generator):
    root_node = parser_with_incremental_int_generator.parse({'seed': '@MyGen'})
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert collected_properties[0]['seed'] == 4


def test_can_use_generator_with_other_params(parser_with_incremental_int_generator):
    root_node = parser_with_incremental_int_generator.parse({
        'wind_speed': [5.0, 7.0],
        'yaw_angle': [0.0, 10.0],
        'seed': 'gen:MyGen'
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert len(collected_properties) == 4
    for i in range(4):
        assert collected_properties[i]['seed'] == 4 + 2*i


def test_generator_persists(parser_with_incremental_int_generator):
    root_node = parser_with_incremental_int_generator.parse({
        'a': {'wind_speed': 4.0, 'seed1': '@MyGen'},
        'b': {'wind_speed': 6.0, 'seed1': '@MyGen', 'seed2': 'gen:MyGen'}
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert collected_properties[0]['seed1'] == 4
    assert collected_properties[1]['seed1'] == 6
    assert collected_properties[1]['seed2'] == 8


def test_generator_does_not_duplicate():
    provider = DictSpecificationProvider({
        'generators': {
            'MyGen': {
                'method': 'IncrementalInt'
            }
        },
        'spec': {
            'a': {'alpha': '@MyGen'},
            'b': {'alpha': '@MyGen', 'beta': '@MyGen'},
            'c': {'alpha': '#repeat(@MyGen, 3)'}
        }
    })
    parser = SpecificationParser(provider)
    root_node = parser.parse().root_node
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert collected_properties[0]['alpha'] == 1
    assert collected_properties[1]['alpha'] == 2
    assert collected_properties[1]['beta'] == 3
    assert collected_properties[2]['alpha'] == 4
    assert collected_properties[3]['alpha'] == 5
    assert collected_properties[4]['alpha'] == 6


def test_emplaces_list_macro_correctly():
    parser = SpecificationNodeParser(value_libraries={'macro': {'3directions': Macro([-8.0, 0.0, 8.0])}})
    root_node = parser.parse({
        'wind_speed': [6.0, 8.0],
        'yaw_angle': '$3directions'
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert len(collected_properties) == 6
    assert collected_properties[0]['wind_speed'] == 6.0
    assert collected_properties[0]['yaw_angle'] == -8.0
    assert collected_properties[1]['wind_speed'] == 6.0
    assert collected_properties[1]['yaw_angle'] == 0.0


def test_emplaces_dict_macro_correctly():
    macro = Macro({
        'rotor_speed': 0.0,
        'simulation_mode': 'idling'
    })
    parser = SpecificationNodeParser(value_libraries={'macro': {'idling': macro}})
    root_node = parser.parse({
        'wind_speed': [6.0, 8.0],
        'irrelevant': 'macro:idling'
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert len(collected_properties) == 2
    assert collected_properties[0]['wind_speed'] == 6.0
    assert collected_properties[1]['wind_speed'] == 8.0
    for p in collected_properties:
        assert p['simulation_mode'] == 'idling'
        assert p['rotor_speed'] == 0.0


def test_raises_lookup_error_if_macro_not_found():
    macro = Macro({
        'rotor_speed': 0.0,
        'simulation_mode': 'idling'
    })
    parser = SpecificationNodeParser(value_libraries={'macro': {'idling': macro}})
    with pytest.raises(LookupError):
        parser.parse({
            'wind_speed': [6.0, 8.0],
            'irrelevant': 'macro:parked'
        })



def test_specification_node_parser_has_correct_path():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'WS{wind_speed}/WD{wind_direction}/TI{turbulence_intensity}',
        'wind_speed': 8.0,
        'directions': [{'wind_direction': 0.0, 'turbulence_intensity': '10%'}, {'wind_direction': 180.0, 'turbulence_intensity': '20%'}]
    })
    expected_paths = [
        'WS8.0/WD0.0/TI10%',
        'WS8.0/WD180.0/TI20%'
    ]
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_specification_node_parser_has_correct_path_with_duplicate_values():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'WS{wind_speed}',
        'wind_speed': 8.0,
        'wind_direction': [0.0, 180.0]
    })
    expected_paths = [
        'WS8.0/a',
        'WS8.0/b'
    ]
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_specification_node_parser_has_correct_path_with_path_format():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'WS{wind_speed:aa}/WD{wind_direction:01}',
        'wind_speed': [8.0, 9.0, 10.0],
        'wind_direction': [0.0, 180.0]
    })
    expected_paths = [
        'WSaa/WD01',
        'WSaa/WD02',
        'WSab/WD01',
        'WSab/WD02',
        'WSac/WD01',
        'WSac/WD02'
    ]
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_specification_node_parser_has_correct_path_when_no_path_defined():
    root_node = DefaultSpecificationNodeParser().parse({
        'wind_speed': [8.0, 9.0, 10.0],
        'wind_direction': [0.0, 180.0]
    })
    expected_paths = ['a', 'b', 'c', 'd', 'e', 'f']
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_node_with_overridden_properties_has_correct_path():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'WS{wind_speed}/WD{wind_direction}',
        'wind_speed': 8.0,
        'wind_directions': {
            'wind_direction': [0.0, 180.0]
        },
        'wind_directions_wind_speed': {
            'wind_direction': [0.0, 180.0],
            'wind_speed': [10.0, 12.0]
        }
    })
    expected_paths = {
        'WS8.0/WD0.0',
        'WS8.0/WD180.0',
        'WS10.0/WD0.0',
        'WS12.0/WD0.0',
        'WS10.0/WD180.0',
        'WS12.0/WD180.0',
    }
    root_node.evaluate()
    assert {leaf.path for leaf in root_node.leaves} == expected_paths

def test_concatenates_paths_in_child_dict():
    root_node = DefaultSpecificationNodeParser().parse({
        'section1': {
            'policy:path': 'section1',
            'blah': {
                'policy:path': '{alpha}',
                'alpha': ['egg', 'tadpole', 'frog']
            }
        }
    })
    expected_paths = {
        'section1/egg',
        'section1/tadpole',
        'section1/frog'
    }
    root_node.evaluate()
    paths = {leaf.path for leaf in root_node.leaves}
    assert paths == expected_paths


def test_concatenates_paths_in_child_dict_parent_has_properties():
    root_node = DefaultSpecificationNodeParser().parse({
        'section1': {
            'policy:path': '{beta}',
            'beta': 42.0,
            'blah': {
                'policy:path': '{alpha}',
                'alpha': ['egg', 'tadpole', 'frog']
            }
        }
    })
    expected_paths = {
        '42.0/egg',
        '42.0/tadpole',
        '42.0/frog'
    }
    root_node.evaluate()
    paths = {leaf.path for leaf in root_node.leaves}
    assert paths == expected_paths


def test_can_produce_range_of_items():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'range': RangeEvaluator}}).parse({
        'wind_speed': '#range(1, 3, 1)'
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 1},
        {'wind_speed': 2},
        {'wind_speed': 3},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_combined_with_list():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'range': RangeEvaluator}}).parse({
        'wind_speed': '#range(1, 3, 1)',
        'wind_direction': [0.0, 180.0]
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 1, 'wind_direction': 0.0},
        {'wind_speed': 1, 'wind_direction': 180.0},
        {'wind_speed': 2, 'wind_direction': 0.0},
        {'wind_speed': 2, 'wind_direction': 180.0},
        {'wind_speed': 3, 'wind_direction': 0.0},
        {'wind_speed': 3, 'wind_direction': 180.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_stopped_at_macro():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'range': RangeEvaluator}, 'macro': {'vref': Macro(4)}}).parse({
        'wind_speed': '#range(1, $vref, 1.5)',
        'wind_direction': [0.0, 180.0]
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 1, 'wind_direction': 0.0},
        {'wind_speed': 1, 'wind_direction': 180.0},
        {'wind_speed': 2.5, 'wind_direction': 0.0},
        {'wind_speed': 2.5, 'wind_direction': 180.0},
        {'wind_speed': 4, 'wind_direction': 0.0},
        {'wind_speed': 4, 'wind_direction': 180.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_use_properties_from_evaluator_in_macro_in_spec_evaluator():
    provider = DictSpecificationProvider({
        'macros': {
            'MyRange': '#range(2, 5, 2)'
        },
        'spec': {
            'alpha': '$MyRange',
            'beta': '#4 + !alpha'
        }
    })
    parser = SpecificationParser(provider)
    root_node = parser.parse().root_node
    expected = [
        {'alpha': 2, 'beta': 6},
        {'alpha': 4, 'beta': 8}
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_combine_macro_list_with_two_other_lists():
    provider = DictSpecificationProvider({
        'macros': {
            'MyRange': [2, 4]
        },
        'spec': {
            'alpha': '$MyRange',
            'beta': [9, 10],
            'gamma': ['tadpole', 'frog']
        }
    })
    parser = SpecificationParser(provider)
    root_node = parser.parse().root_node
    expected = [
        {'alpha': 2, 'beta': 9, 'gamma': 'tadpole'},
        {'alpha': 2, 'beta': 9, 'gamma': 'frog'},
        {'alpha': 2, 'beta': 10, 'gamma': 'tadpole'},
        {'alpha': 2, 'beta': 10, 'gamma': 'frog'},
        {'alpha': 4, 'beta': 9, 'gamma': 'tadpole'},
        {'alpha': 4, 'beta': 9, 'gamma': 'frog'},
        {'alpha': 4, 'beta': 10, 'gamma': 'tadpole'},
        {'alpha': 4, 'beta': 10, 'gamma': 'frog'}
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties


def test_path_is_right_when_using_object_in_macro():
    provider = DictSpecificationProvider({
        'macros': {
            'DoSomething': {
                'firstly': 'this',
                'secondly': 2
            }
        },
        'spec': {
            'blah': {
                'policy:path': 'my_path',
                'blo': '$DoSomething'
            }
        }
    })
    parser = SpecificationParser(provider)
    root_node = parser.parse().root_node
    leaves = root_node.leaves
    assert len(leaves) == 1
    assert leaves[0].path == 'my_path'


def test_uses_object_in_macro_successfully():
    provider = DictSpecificationProvider({
        'macros': {
            'DoSomething': {
                'firstly': 'this',
                'secondly': 2
            }
        },
        'spec': {
            'blah': {
                'blo': '$DoSomething',
                'gamma': [1, 2, 3],
                'delta': ['a', 'b']
            }
        }
    })
    parser = SpecificationParser(provider)
    root_node = parser.parse().root_node
    leaves = root_node.leaves
    assert len(leaves) == 6
    for l in leaves:
        collected_properties = l.collected_properties
        assert collected_properties['firstly'] == 'this'
        assert collected_properties['secondly'] == 2
        assert 'gamma' in collected_properties
        assert 'delta' in collected_properties


def test_can_do_multiplication_with_evaluator():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'mult': MultiplyEvaluator}, 'macro': {'vref': Macro(4)}}).parse({
        'wind_speed': '#5 * 3',
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 15.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_multiply_property():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'mult': MultiplyEvaluator}, 'macro': {'vref': Macro(4)}}).parse({
        'wind_speed': [0.0, 10.0, 20.0],
        'wind_direction': '!wind_speed * 18'
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 0.0, 'wind_direction': 0.0},
        {'wind_speed': 10.0, 'wind_direction': 180.0},
        {'wind_speed': 20.0, 'wind_direction': 360.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_multiply_macro():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'mult': MultiplyEvaluator}, 'macro': {'vref': Macro(4)}}).parse({
        'wind_speed': [0.0, 10.0, 20.0],
        'wind_direction': '$vref * 1.5'
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 0.0, 'wind_direction': 6.0},
        {'wind_speed': 10.0, 'wind_direction': 6.0},
        {'wind_speed': 20.0, 'wind_direction': 6.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_stopped_at_property():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'range': RangeEvaluator}, 'macro': {'vref': Macro(4)}}).parse({
        'top_speed': [1.5, 3.0, '$vref'],
        'wind_speed': '#range(0, !top_speed, 1.5)',
    })
    root_node.evaluate()
    expected = [
        {'top_speed': 1.5, 'wind_speed': 0.0},
        {'top_speed': 1.5, 'wind_speed': 1.5},
        {'top_speed': 3.0, 'wind_speed': 0.0},
        {'top_speed': 3.0, 'wind_speed': 1.5},
        {'top_speed': 3.0, 'wind_speed': 3.0},
        {'top_speed': 4.0, 'wind_speed': 0.0},
        {'top_speed': 4.0, 'wind_speed': 1.5},
        {'top_speed': 4.0, 'wind_speed': 3.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_stopped_at_ghost():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'range': RangeEvaluator}, 'macro': {'vref': Macro(4)}}).parse({
        '_top_speed': 4.5,
        'wind_speed': '#range(0, !top_speed, 1.5)',
    })
    root_node.evaluate()
    expected = [
        {'wind_speed': 0.0},
        {'wind_speed': 1.5},
        {'wind_speed': 3.0},
        {'wind_speed': 4.5},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_ghost_parameters_appear_on_leaf_nodes():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'WS{wind_speed}/WD{wind_direction}',
        'wind_speed': 8.0,
        'wind_direction': [13.0, 15.0],
        '_greeting': 'hello turbine'
    })

    assert all(l.ghosts == {'greeting': 'hello turbine'} for l in root_node.leaves)

def test_ghost_parameters_are_overwritten_lower_down():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'WS{wind_speed}/WD{wind_direction}',
        'wind_speed': 8.0,
        '_greeting': 'hello turbine',
        '_wind_speed': 'breezy',
        'dlc1.1': {
            'wind_direction': 3.0,
        },
        'dlc1.2': {
            '_wind_speed': 'gusty',
            'wind_direction': 13.0,
        }
    })

    expected_ghosts = [
        {
            'greeting': 'hello turbine',
            'wind_speed': 'breezy'
        },
        {
            'greeting': 'hello turbine',
            'wind_speed': 'gusty'
        }
    ]

    assert [l.ghosts for l in root_node.leaves] == expected_ghosts

def test_can_use_macro_list_elements_in_addition():
    root_node = DefaultSpecificationNodeParser(value_libraries={'eval': {'add': AddEvaluator}, 'macro': {'List': Macro([3, 5])}}).parse({
        'base_value': '$List',
        'total_value': '!base_value + 4'
    })
    root_node.evaluate()
    expected = [
        {'base_value': 3, 'total_value': 7},
        {'base_value': 5, 'total_value': 9}
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_adding_index_property_produces_index_node():
    root_node = DefaultSpecificationNodeParser().parse({
        'pitch[1]': 2.3
    })

    assert isinstance(root_node.leaves[0], IndexedNode)
    assert root_node.leaves[0].index == 1
    assert root_node.leaves[0].property_name == 'pitch'
    assert root_node.leaves[0].property_value == 2.3
