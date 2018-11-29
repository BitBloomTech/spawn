from multiwindcalc.specification.specification import *

def test_returns_normal_node_for_normal_name():
    node = SpecificationNodeFactory().create(None, 'pitch', 42, None, {})
    assert type(node) == SpecificationNode
    assert node.property_name == 'pitch'
    assert node.property_value == 42

def test_returns_indexed_node_for_index_pattern_name():
    node = SpecificationNodeFactory().create(None, 'pitch[1]', 42, None, {})
    assert type(node) == IndexedNode
    assert node.index == 1
    assert node.property_name == 'pitch'
    assert node.property_value == 42
