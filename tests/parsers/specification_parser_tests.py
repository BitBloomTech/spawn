import pytest
from multiwindcalc.parsers.specification import *

def test_parse_null_node_returns_root_node_no_children():
    node = SpecificationNodeParser().parse(None)
    assert node.is_root
    assert node.children == []

def test_parse_single_value_returns_correct_tree():
    root_node = SpecificationNodeParser().parse({'wind_speed': 8.0})
    assert root_node.is_root
    assert len(root_node.children) == 1
    node = root_node.children[0]
    assert node.property_name == 'wind_speed'
    assert node.property_value == 8.0
    assert node.children == []

def test_parse_multiple_values_returns_root_with_multiple_children():
    values = [8.0, 10.0, 12.0]
    root_node = SpecificationNodeParser().parse({'wind_speed': values})
    assert root_node.is_root
    assert len(root_node.children) == 3
    for i, expected_value in enumerate(values):
        node = root_node.children[i]
        assert node.property_name == 'wind_speed'
        assert node.property_value == expected_value
        assert node.children == []

def test_parse_multiple_properties_returns_multiple_levels():
    root_node = SpecificationNodeParser().parse({'wind_speed': 8.0, 'turbulence_intensity': '10%'})
    assert len(root_node.children) == 1
    assert root_node.children[0].property_name == 'wind_speed'
    assert root_node.children[0].property_value == 8.0
    assert len(root_node.children[0].children) == 1
    assert root_node.children[0].children[0].property_name == 'turbulence_intensity'
    assert root_node.children[0].children[0].property_value == '10%'

def test_parse_multiple_properties_returns_correct_leaf_nodes():
    root_node = SpecificationNodeParser().parse({'wind_speed': [8.0, 12.0], 'turbulence_intensity': ['10%', '20%']})
    assert len(root_node.children) == 2
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
    root_node = SpecificationNodeParser().parse({'wind_speed': 8.0, 'direction_0': {'wind_direction': 0.0, 'turbulence_intensity': '10%'}, 'direction_1': {'wind_direction': 180.0, 'turbulence_intensity': '20%'}})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0, 'turbulence_intensity': '10%'},
        {'wind_speed': 8.0, 'wind_direction': 180.0, 'turbulence_intensity': '20%'}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    print(collected_properties)
    for expected in expected_args:
        assert expected in collected_properties

def test_parse_child_node_list_produces_correct_combinations():
    root_node = SpecificationNodeParser().parse({'wind_speed': 8.0, 'directions': [{'wind_direction': 0.0, 'turbulence_intensity': '10%'}, {'wind_direction': 180.0, 'turbulence_intensity': '20%'}]})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0, 'turbulence_intensity': '10%'},
        {'wind_speed': 8.0, 'wind_direction': 180.0, 'turbulence_intensity': '20%'}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    for expected in expected_args:
        assert expected in collected_properties

def test_parse_with_zip_function_produces_pairs():
    root_node = SpecificationNodeParser().parse({'zip': {'wind_speed': [8.0, 10.0], 'wind_direction': [0.0, 180.0]}})
    expected_args = [
        {'wind_speed': 8.0, 'wind_direction': 0.0},
        {'wind_speed': 10.0, 'wind_direction': 180.0}
    ]
    collected_properties = [leaf.collected_properties for leaf in root_node.leaves]
    for expected in expected_args:
        assert expected in collected_properties


def test_zip_function_raises_error_if_lists_have_unequal_size():
    with pytest.raises(RuntimeError):
        SpecificationNodeParser().parse({'zip': {'wind_speed': [8.0, 10.0, 12.0], 'wind_direction': [0.0, 180.0]}})
