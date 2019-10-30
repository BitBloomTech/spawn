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
import json

from spawn.specification.generator_methods import *
from spawn.parsers.specification_parser import *
from spawn.specification.specification import *
from spawn.specification.value_proxy import *
from spawn.errors import *

@pytest.fixture
def parser(plugin_loader):
    return SpecificationParser(plugin_loader)

class DefaultSpecificationNodeParser(SpecificationNodeParser):
    def __init__(self, **kwargs):
        super().__init__(
            value_proxy_parser=ValueProxyParser(kwargs.get('value_libraries', ValueLibraries())),
            combinators={'zip': zip_properties, 'product': product}, default_combinator='product'
        )

def test_parse_null_node_returns_root_node_no_children():
    node = DefaultSpecificationNodeParser().parse(None)
    assert node.is_root
    assert node.children == []

def test_parse_single_value_returns_correct_tree():
    root_node = DefaultSpecificationNodeParser().parse({'alpha': 8.0})
    assert root_node.is_root
    assert len(root_node.children) == 1
    node = root_node.children[0]
    assert node.property_name == 'alpha'
    assert node.property_value == 8.0
    assert node.children == []

def test_parse_multiple_values_returns_root_with_multiple_children():
    values = [8.0, 10.0, 12.0]
    root_node = DefaultSpecificationNodeParser().parse({'alpha': values})
    assert root_node.is_root
    assert len(root_node.children) == 3
    for i, expected_value in enumerate(values):
        node = root_node.children[i]
        assert node.property_name == 'alpha'
        assert node.property_value == expected_value
        assert node.children == []

def test_parse_multiple_properties_returns_multiple_levels():
    root_node = DefaultSpecificationNodeParser().parse({'alpha': 8.0, 'beta': '10%'})
    assert len(root_node.children) == 1
    assert root_node.children[0].property_name == 'alpha'
    assert root_node.children[0].property_value == 8.0
    assert len(root_node.children[0].children) == 1
    assert root_node.children[0].children[0].property_name == 'beta'
    assert root_node.children[0].children[0].property_value == '10%'

def test_parse_multiple_properties_returns_correct_leaf_nodes():
    root_node = DefaultSpecificationNodeParser().parse({'alpha': [8.0, 12.0], 'beta': ['10%', '20%']})
    assert len(root_node.leaves) == 4
    expected_args = [
        {'alpha': 8.0, 'beta': '10%'},
        {'alpha': 12.0, 'beta': '10%'},
        {'alpha': 8.0, 'beta': '20%'},
        {'alpha': 12.0, 'beta': '20%'},
    ]
    for leaf in root_node.leaves:
        expected_args.remove(leaf.collected_properties)
    assert expected_args == []

def test_parse_child_nodes_produces_correct_combinations():
    root_node = DefaultSpecificationNodeParser().parse({'alpha': 8.0, 'section_0': {'gamma': 0.0, 'beta': '10%'}, 'section_1': {'gamma': 180.0, 'beta': '20%'}})
    expected_args = [
        {'alpha': 8.0, 'gamma': 0.0, 'beta': '10%'},
        {'alpha': 8.0, 'gamma': 180.0, 'beta': '20%'}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    for expected in expected_args:
        assert expected in collected_properties

def test_parse_child_node_list_produces_correct_combinations():
    root_node = DefaultSpecificationNodeParser().parse({'alpha': 8.0, 'sections': [{'gamma': 0.0, 'beta': '10%'}, {'gamma': 180.0, 'beta': '20%'}]})
    expected_args = [
        {'alpha': 8.0, 'gamma': 0.0, 'beta': '10%'},
        {'alpha': 8.0, 'gamma': 180.0, 'beta': '20%'}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    for expected in expected_args:
        assert expected in collected_properties

def test_parse_with_zip_function_produces_pairs():
    root_node = DefaultSpecificationNodeParser().parse({'combine:zip': {'alpha': [8.0, 10.0], 'gamma': [0.0, 180.0]}})
    expected_args = [
        {'alpha': 8.0, 'gamma': 0.0},
        {'alpha': 10.0, 'gamma': 180.0}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert expected_args == collected_properties

def test_parse_with_product_function_produces_pairs():
    root_node = DefaultSpecificationNodeParser().parse({'combine:product': {'alpha': [8.0, 10.0], 'gamma': [0.0, 180.0]}})
    expected_args = [
        {'alpha': 8.0, 'gamma': 0.0},
        {'alpha': 8.0, 'gamma': 180.0},
        {'alpha': 10.0, 'gamma': 0.0},
        {'alpha': 10.0, 'gamma': 180.0}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert expected_args == collected_properties

def test_parse_with_implicit_product_and_zip_produces_expected_output():
    root_node = DefaultSpecificationNodeParser().parse({'alpha': [8.0, 10.0], 'combine:zip': { 'gamma': [0.0, 180.0], 'beta': ['0%', '20%']}})
    expected_args = [
        {'alpha': 8.0, 'gamma': 0.0, 'beta': '0%'},
        {'alpha': 8.0, 'gamma': 180.0, 'beta': '20%'},
        {'alpha': 10.0, 'gamma': 0.0, 'beta': '0%'},
        {'alpha': 10.0, 'gamma': 180.0, 'beta': '20%'},
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert expected_args == collected_properties

def test_zip_function_raises_error_if_lists_have_unequal_size():
    with pytest.raises(ValueError):
        DefaultSpecificationNodeParser().parse({'combine:zip': {'alpha': [8.0, 10.0, 12.0], 'gamma': [0.0, 180.0]}})

@pytest.fixture(scope='function')
def parser_with_incremental_int_generator():
    generator_library = {
        'MyGen': IncrementalInt(4, 2)
    }
    return DefaultSpecificationNodeParser(value_libraries=ValueLibraries(generators=generator_library))


def test_can_use_generator_once(parser_with_incremental_int_generator):
    root_node = parser_with_incremental_int_generator.parse({'seed': '@MyGen'})
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert collected_properties[0]['seed'] == 4


def test_can_use_generator_with_other_params(parser_with_incremental_int_generator):
    root_node = parser_with_incremental_int_generator.parse({
        'alpha': [5.0, 7.0],
        'beta': [0.0, 10.0],
        'seed': 'gen:MyGen'
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert len(collected_properties) == 4
    for i in range(4):
        assert collected_properties[i]['seed'] == 4 + 2*i


def test_generator_persists(parser_with_incremental_int_generator):
    root_node = parser_with_incremental_int_generator.parse({
        'a': {'alpha': 4.0, 'seed1': '@MyGen'},
        'b': {'alpha': 6.0, 'seed1': '@MyGen', 'seed2': 'gen:MyGen'}
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert collected_properties[0]['seed1'] == 4
    assert collected_properties[1]['seed1'] == 6
    assert collected_properties[1]['seed2'] == 8


def test_generator_does_not_duplicate(parser):
    description = {
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
    }
    root_node = parser.parse(description).root_node
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert collected_properties[0]['alpha'] == 1
    assert collected_properties[1]['alpha'] == 2
    assert collected_properties[1]['beta'] == 3
    assert collected_properties[2]['alpha'] == 4
    assert collected_properties[3]['alpha'] == 5
    assert collected_properties[4]['alpha'] == 6


def test_emplaces_list_macro_correctly():
    parser = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(macros={'3sections': Macro([-8.0, 0.0, 8.0])}))
    root_node = parser.parse({
        'alpha': [6.0, 8.0],
        'beta': '$3sections'
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert len(collected_properties) == 6
    assert collected_properties[0]['alpha'] == 6.0
    assert collected_properties[0]['beta'] == -8.0
    assert collected_properties[1]['alpha'] == 6.0
    assert collected_properties[1]['beta'] == 0.0


def test_emplaces_dict_macro_correctly():
    macro = Macro({
        'beta': 0.0,
        'gamma': 'idling'
    })
    parser = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(macros={'idling': macro}))
    root_node = parser.parse({
        'alpha': [6.0, 8.0],
        'irrelevant': 'macro:idling'
    })
    root_node.evaluate()
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    assert len(collected_properties) == 2
    assert collected_properties[0]['alpha'] == 6.0
    assert collected_properties[1]['alpha'] == 8.0
    for p in collected_properties:
        assert p['gamma'] == 'idling'
        assert p['beta'] == 0.0


def test_specification_node_parser_has_correct_path():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'a{alpha}/b{beta}/c{gamma}',
        'alpha': 8.0,
        'sections': [{'gamma': 0.0, 'beta': '10%'}, {'gamma': 180.0, 'beta': '20%'}]
    })
    expected_paths = [
        'a8.0/b10%/c0.0',
        'a8.0/b20%/c180.0'
    ]
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_specification_node_parser_has_correct_path_with_duplicate_values():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'a{alpha}',
        'alpha': 8.0,
        'gamma': [0.0, 180.0]
    })
    expected_paths = [
        'a8.0/a',
        'a8.0/b'
    ]
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_specification_node_parser_has_correct_path_with_path_format():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'X{alpha:aa}/Y{gamma:01}',
        'alpha': [8.0, 9.0, 10.0],
        'gamma': [0.0, 180.0]
    })
    expected_paths = [
        'Xaa/Y01',
        'Xaa/Y02',
        'Xab/Y01',
        'Xab/Y02',
        'Xac/Y01',
        'Xac/Y02'
    ]
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_specification_node_parser_has_correct_path_when_no_path_defined():
    root_node = DefaultSpecificationNodeParser().parse({
        'alpha': [8.0, 9.0, 10.0],
        'gamma': [0.0, 180.0]
    })
    expected_paths = ['a', 'b', 'c', 'd', 'e', 'f']
    paths = [leaf.path for leaf in root_node.leaves]
    assert paths == expected_paths

def test_node_with_overridden_properties_has_correct_path():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'X{alpha}/Y{gamma}',
        'alpha': 8.0,
        'gammas': {
            'gamma': [0.0, 180.0]
        },
        'gammas_alphas': {
            'gamma': [0.0, 180.0],
            'alpha': [10.0, 12.0]
        }
    })
    expected_paths = {
        'X8.0/Y0.0',
        'X8.0/Y180.0',
        'X10.0/Y0.0',
        'X12.0/Y0.0',
        'X10.0/Y180.0',
        'X12.0/Y180.0',
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
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'range': RangeEvaluator})).parse({
        'alpha': '#range(1, 3, 1)'
    })
    root_node.evaluate()
    expected = [
        {'alpha': 1},
        {'alpha': 2},
        {'alpha': 3},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_combined_with_list():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'range': RangeEvaluator})).parse({
        'alpha': '#range(1, 3, 1)',
        'gamma': [0.0, 180.0]
    })
    root_node.evaluate()
    expected = [
        {'alpha': 1, 'gamma': 0.0},
        {'alpha': 1, 'gamma': 180.0},
        {'alpha': 2, 'gamma': 0.0},
        {'alpha': 2, 'gamma': 180.0},
        {'alpha': 3, 'gamma': 0.0},
        {'alpha': 3, 'gamma': 180.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_stopped_at_macro():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'range': RangeEvaluator}, macros={'vref': Macro(4)})).parse({
        'alpha': '#range(1, $vref, 1.5)',
        'gamma': [0.0, 180.0]
    })
    root_node.evaluate()
    expected = [
        {'alpha': 1, 'gamma': 0.0},
        {'alpha': 1, 'gamma': 180.0},
        {'alpha': 2.5, 'gamma': 0.0},
        {'alpha': 2.5, 'gamma': 180.0},
        {'alpha': 4, 'gamma': 0.0},
        {'alpha': 4, 'gamma': 180.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_use_properties_from_evaluator_in_macro_in_spec_evaluator(parser):
    description = {
        'macros': {
            'MyRange': '#range(2, 5, 2)'
        },
        'spec': {
            'alpha': '$MyRange',
            'beta': '#4 + !alpha'
        }
    }
    root_node = parser.parse(description).root_node
    expected = [
        {'alpha': 2, 'beta': 6},
        {'alpha': 4, 'beta': 8}
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_combine_macro_list_with_two_other_lists(parser):
    description = {
        'macros': {
            'MyRange': [2, 4]
        },
        'spec': {
            'alpha': '$MyRange',
            'beta': [9, 10],
            'gamma': ['tadpole', 'frog']
        }
    }
    root_node = parser.parse(description).root_node
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


def test_path_is_right_when_using_object_in_macro(parser):
    description = {
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
    }
    root_node = parser.parse(description).root_node
    leaves = root_node.leaves
    assert len(leaves) == 1
    assert leaves[0].path == 'my_path'


def test_uses_object_in_macro_successfully(parser):
    description = {
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
    }
    root_node = parser.parse(description).root_node
    leaves = root_node.leaves
    assert len(leaves) == 6
    for l in leaves:
        collected_properties = l.collected_properties
        assert collected_properties['firstly'] == 'this'
        assert collected_properties['secondly'] == 2
        assert 'gamma' in collected_properties
        assert 'delta' in collected_properties


def test_macros_are_recursively_evaluated(parser):
    root_node = parser.parse({
        'macros': {
            'Ref': 1,
            'Something': {
                'alpha': '$Ref'
            }
        },
        'spec': {
            'blah': '$Something'
        }
    }).root_node
    leaves = root_node.leaves
    assert len(leaves) == 1
    assert leaves[0].collected_properties == {'alpha': 1}


def test_can_do_multiplication_with_evaluator():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'mult': MultiplyEvaluator}, macros={'vref': Macro(4)})).parse({
        'alpha': '#5 * 3',
    })
    root_node.evaluate()
    expected = [
        {'alpha': 15.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_multiply_property():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'mult': MultiplyEvaluator}, macros={'vref': Macro(4)})).parse({
        'alpha': [0.0, 10.0, 20.0],
        'gamma': '!alpha * 18'
    })
    root_node.evaluate()
    expected = [
        {'alpha': 0.0, 'gamma': 0.0},
        {'alpha': 10.0, 'gamma': 180.0},
        {'alpha': 20.0, 'gamma': 360.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_multiply_macro():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'mult': MultiplyEvaluator}, macros={'vref': Macro(4)})).parse({
        'alpha': [0.0, 10.0, 20.0],
        'gamma': '$vref * 1.5'
    })
    root_node.evaluate()
    expected = [
        {'alpha': 0.0, 'gamma': 6.0},
        {'alpha': 10.0, 'gamma': 6.0},
        {'alpha': 20.0, 'gamma': 6.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_stopped_at_property():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'range': RangeEvaluator}, macros={'vref': Macro(4)})).parse({
        'top_speed': [1.5, 3.0, '$vref'],
        'alpha': '#range(0, !top_speed, 1.5)',
    })
    root_node.evaluate()
    expected = [
        {'top_speed': 1.5, 'alpha': 0.0},
        {'top_speed': 1.5, 'alpha': 1.5},
        {'top_speed': 3.0, 'alpha': 0.0},
        {'top_speed': 3.0, 'alpha': 1.5},
        {'top_speed': 3.0, 'alpha': 3.0},
        {'top_speed': 4.0, 'alpha': 0.0},
        {'top_speed': 4.0, 'alpha': 1.5},
        {'top_speed': 4.0, 'alpha': 3.0},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_can_produce_range_of_items_stopped_at_ghost():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'range': RangeEvaluator}, macros={'vref': Macro(4)})).parse({
        '_top_speed': 4.5,
        'alpha': '#range(0, !top_speed, 1.5)',
    })
    root_node.evaluate()
    expected = [
        {'alpha': 0.0},
        {'alpha': 1.5},
        {'alpha': 3.0},
        {'alpha': 4.5},
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_ghost_parameters_appear_on_leaf_nodes():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'X{alpha}/Y{gamma}',
        'alpha': 8.0,
        'gamma': [13.0, 15.0],
        '_greeting': 'hello pond'
    })

    assert all(l.ghosts == {'greeting': 'hello pond'} for l in root_node.leaves)

def test_ghost_parameters_are_overwritten_lower_down():
    root_node = DefaultSpecificationNodeParser().parse({
        'policy:path': 'a{alpha}/c{gamma}',
        'alpha': 8.0,
        '_greeting': 'hello pond',
        '_spawning': 'tadpole',
        'dlc1.1': {
            'gamma': 3.0,
        },
        'dlc1.2': {
            '_spawning': 'frog',
            'gamma': 13.0,
        }
    })

    expected_ghosts = [
        {
            'greeting': 'hello pond',
            'spawning': 'tadpole'
        },
        {
            'greeting': 'hello pond',
            'spawning': 'frog'
        }
    ]

    assert [l.ghosts for l in root_node.leaves] == expected_ghosts

def test_can_use_macro_list_elements_in_addition():
    root_node = DefaultSpecificationNodeParser(value_libraries=ValueLibraries(evaluators={'add': AddEvaluator}, macros={'List': Macro([3, 5])})).parse({
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
        'alpha[1]': 2.3
    })

    assert isinstance(root_node.leaves[0], IndexedNode)
    assert root_node.leaves[0].index == 1
    assert root_node.leaves[0].property_name == 'alpha'
    assert root_node.leaves[0].property_value == 2.3

def test_can_have_multiple_indexed_properties_with_one_being_a_macro(parser):
    description = {
        'macros': {
            'Value': 4.0
        },
        'spec': {
            'blah': {
                'alpha[1]': '$Value',
                'beta[1]': 6
            }
        }
    }
    root_node = parser.parse(description).root_node
    assert isinstance(root_node.leaves[0], IndexedNode)

def test_missing_macro_raises_macro_not_found_error(parser):
    description = {
        'spec': {
            'blah': {
                'alpha': '$Value'
            }
        }
    }
    with pytest.raises(MacroNotFoundError) as e:
        parser.parse(description)
    assert str(e.value) == 'Macro "Value" not found'

def test_missing_generator_raises_generator_not_found_error(parser):
    description = {
        'spec': {
            'blah': {
                'alpha': '@Generate'
            }
        }
    }
    with pytest.raises(GeneratorNotFoundError) as e:
        parser.parse(description)
    assert str(e.value) == 'Generator "Generate" not found'

def test_missing_evaluator_raises_evaluator_not_found_error(parser):
    description = {
        'spec': {
            'blah': {
                'alpha': '#Evaluate()'
            }
        }
    }
    with pytest.raises(EvaluatorNotFoundError) as e:
        parser.parse(description).root_node
    assert str(e.value) == 'Evaluator "Evaluate" not found'

def test_evaluator_with_incorrect_args_raises_evaluator_type_error(parser):
    description = {
        'spec': {
            'blah': {
                'alpha': '#range(1, 2, 3, 4)'
            }
        }
    }
    with pytest.raises(EvaluatorTypeError) as e:
        parser.parse(description)
    assert str(e.value) == 'range() takes the following arguments: start, end, step (1, 2, 3, 4 provided)'

def test_invalid_operator_raises_invalid_operator_error(parser):
    description = {
        'spec': {
            'blah': {
                'alpha': '#1 // 2'
            }
        }
    }
    with pytest.raises(InvalidOperatorError) as e:
        parser.parse(description)
    assert str(e.value) == 'Invalid operator in 1 // 2 near position 0'

@pytest.mark.parametrize('description, error', [
    ({}, '"spec" node not found in description'),
    ({'spec': ['a', 'b']}, '"spec" node should be of type dict'),
    ({'spec': {}}, '"spec" node is empty')
])
def test_spec_format_error_raised_for_invalid_description(parser, description, error):
    with pytest.raises(SpecFormatError) as e:
        parser.parse(description)
    assert str(e.value) == 'Invalid spec format: {}'.format(error)

_literals = [
    [4, 5, 6],
    {'delta': 1, 'epsilon': 2},
    '$NotAMacro',
    '@NotAGenerator',
    '#NotAnEvaluator',
    '!this is not an equation'
]
@pytest.mark.parametrize('literal_value', _literals)
def test_key_literal_properties_are_not_expanded(literal_value):
    root_node = DefaultSpecificationNodeParser().parse({
        'alpha': {
            'beta': ['egg', 'tadpole'],
            '~gamma': literal_value
        }
    })
    root_node.evaluate()
    expected = [
        {'beta': 'egg', 'gamma': literal_value},
        {'beta': 'tadpole', 'gamma': literal_value}
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

@pytest.mark.parametrize('literal_value', _literals)
def test_value_literal_properties_are_not_expanded(literal_value):
    root_node = DefaultSpecificationNodeParser().parse({
        'alpha': {
            'beta': ['egg', 'tadpole'],
            'gamma': '~' + (literal_value if isinstance(literal_value, str) else json.dumps(literal_value))
        }
    })
    root_node.evaluate()
    expected = [
        {'beta': 'egg', 'gamma': literal_value},
        {'beta': 'tadpole', 'gamma': literal_value}
    ]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties

def test_with_literal_key_and_value_value_is_unchanged():
    s = '~I just like tildes OK!'
    root_node = DefaultSpecificationNodeParser().parse({
        '~alpha': s
    })
    root_node.evaluate()
    expected = [{'alpha': s}]
    properties = [l.collected_properties for l in root_node.leaves]
    assert expected == properties
