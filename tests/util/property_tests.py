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

from multiwindcalc.util.property import *

class Dummy:
    def __init__(self):
        self._decorated_int = 42
        self._decorated_array = [None, None, None]
        self._validated_array = [None, None, None]

    basic_int = IntProperty()
    basic_float = FloatProperty()
    basic_string = StringProperty()

    range_int = IntProperty(min=0, max=10)
    range_float = FloatProperty(min=0.0, max=10.0)

    possible_values_string = StringProperty(possible_values=['a', 'b', 'c'])
    regex_string = StringProperty(regex='[a-z]+')

    abstract_int = IntProperty(abstract=True)

    float_list = ArrayProperty(float)

    @StringProperty(readonly=True)
    def readonly_string(self):
        return 'I am readonly'

    @int_property
    def decorated_int(self):
        """This is a decorated int"""
        return self._decorated_int
    
    @decorated_int.setter
    def decorated_int(self, value):
        self._decorated_int = value
    
    @decorated_int.validator
    def decorated_int(self, value):
        if value % 3 != 0:
            raise ValueError('{} % 3 != 0'.format(value))
    
    @decorated_int.deleter
    def decorated_int(self):
        self._decorated_int = 0

    @ArrayProperty(float)
    def decorated_array(self, index):
        return self._decorated_array[index]
    
    @decorated_array.setter
    def decorated_array(self, index, value):
        self._decorated_array[index] = value

    @ArrayProperty(int)
    def validated_array(self, index):
        return self._validated_array[index]
    
    @validated_array.setter
    def validated_array(self, index, value):
        self._validated_array[index] = value
    
    @validated_array.validator
    def validated_array(self, index, value):
        if value % 2 != 0:
            raise ValueError('Must be even!')

class DummyDerived(Dummy):
    def __init__(self):
        super().__init__()
        self._overridden_int = 0
        self._overridden_string = 'hello, override'

    @Dummy.basic_int.getter
    def basic_int(self):
        return self._overridden_int
    
    @basic_int.setter
    def basic_int(self, value):
        self._overridden_int = value
    
    @Dummy.basic_float.validator
    def basic_float(self, value):
        if value > 42.0:
            raise ValueError('{} > 42.0'.format(value))
    
    def get_basic_string(self):
        return self._overridden_string
    
    def set_basic_string(self, value):
        self._overridden_string = value.lower()
    
    def validate_basic_string(self, value):
        if not value.lower().startswith('hello'):
            raise ValueError('{} must start with hello'.format(value))
    
    def delete_basic_string(self):
        self._overridden_string = 'hello, deleted'

@pytest.fixture
def obj():
    return Dummy()

@pytest.fixture
def derived_obj():
    return DummyDerived()

@pytest.mark.parametrize('property_name,value', [
    ('basic_int', None),
    ('basic_float', None),
    ('basic_string', None),
])
def test_basic_properties_have_correct_defaults(obj, property_name, value):
    assert getattr(obj, property_name) == value

@pytest.mark.parametrize('property_name,value', [
    ('basic_int', 42),
    ('basic_float', 42.24),
    ('basic_string', 'hello world'),
])
def test_can_set_basic_properties(obj, property_name, value):
    setattr(obj, property_name, value)
    assert getattr(obj, property_name) == value

@pytest.mark.parametrize('property_name,value', [
    ('basic_int', 42.24),
    ('basic_float', 42),
    ('basic_string', 3.141),
])
def test_cannot_set_property_to_wrong_type(obj, property_name, value):
    with pytest.raises(TypeError):
        setattr(obj, property_name, value)

@pytest.mark.parametrize('property_name,value', [
    ('range_int', 5),
    ('range_float', 5.0),
])
def test_can_set_value_inside_of_range(obj, property_name, value):
    setattr(obj, property_name, value)
    assert getattr(obj, property_name) == value

@pytest.mark.parametrize('property_name,value', [
    ('range_int', 42),
    ('range_int', -42),
    ('range_float', 42.24),
    ('range_float', -42.24),
])
def test_cannot_set_value_outside_of_range(obj, property_name, value):
    with pytest.raises(ValueError):
        setattr(obj, property_name, value)

def test_can_set_value_in_possible_values(obj):
    obj.possible_values_string = 'a'
    assert obj.possible_values_string == 'a'

def test_cannot_set_value_outside_possible_values(obj):
    with pytest.raises(ValueError):
        obj.possible_values_string = 'd'

def test_can_set_matching_string_value(obj):
    obj.regex_string = 'abcdefg'
    assert obj.regex_string == 'abcdefg'

def test_cannot_set_non_matching_string_value(obj):
    with pytest.raises(ValueError):
        obj.regex_string = '123456'

def test_get_decorated_int_returns_default_value(obj):
    assert obj.decorated_int == 42

def test_set_decorated_int_raises_type_error_with_invalid_type(obj):
    with pytest.raises(TypeError):
        obj.decorated_int = 'hello'

def test_decorated_property_has_correct_doc(obj):
    assert type(obj).decorated_int.__doc__ == "This is a decorated int"


def test_custom_validation_method_raises_if_invalid(obj):
    with pytest.raises(ValueError):
        obj.decorated_int = 13

def test_can_set_valid_value_on_decorated_int(obj):
    obj.decorated_int = 12  
    assert obj.decorated_int == 12

def test_deleting_a_set_object_sets_value_to_none(obj):
    obj.basic_int = 42
    del obj.basic_int
    assert obj.basic_int == None

def test_custom_deleter_resets_value_to_default(obj):
    obj.decorated_int = 12
    del obj.decorated_int
    assert obj.decorated_int == 0

def test_getter_and_setter_can_be_overridden(obj, derived_obj):
    assert obj.basic_int is None
    assert derived_obj.basic_int == 0
    derived_obj.basic_int = 42
    assert derived_obj.basic_int == 42

def test_overridden_validator_raises_value_error_with_invalid_value(derived_obj):
    with pytest.raises(ValueError):
        derived_obj.basic_float = 43.0

def test_overridden_validator_allows_valid_values(derived_obj):
    derived_obj.basic_float = 42.0
    assert derived_obj.basic_float == 42.0

def test_method_overridden_property_has_correct_default(derived_obj):
    assert derived_obj.basic_string == 'hello, override'

def test_method_overridden_property_can_be_set(derived_obj):
    derived_obj.basic_string = 'hello, basic string'
    assert derived_obj.basic_string == 'hello, basic string'
    
def test_method_overridden_property_raises_value_error_for_invalid_value(derived_obj):
    with pytest.raises(ValueError):
        derived_obj.basic_string = 'goodbye, basic string'

def test_delete_method_overridden_property_correctly_sets_property(derived_obj):
    del derived_obj.basic_string
    assert derived_obj.basic_string == 'hello, deleted'

def test_abstract_property_raises_not_implemented_error_for_get(derived_obj):
    with pytest.raises(NotImplementedError):
        _ = derived_obj.abstract_int

def test_abstract_property_raises_not_implemented_error_for_set(derived_obj):
    with pytest.raises(NotImplementedError):
        derived_obj.abstract_int = 42

def test_abstract_property_raises_not_implemented_error_for_delete(derived_obj):
    with pytest.raises(NotImplementedError):
        del derived_obj.abstract_int

def test_cannot_set_readonly_property(obj):
    with pytest.raises(NotImplementedError):
        obj.readonly_string = 'I changed you!'

def test_can_get_readonly_property(obj):
    assert obj.readonly_string == 'I am readonly'

def test_can_set_float_list_index(obj):
    obj.float_list[0] = 42.0
    assert obj.float_list[0] == 42.0

def test_can_set_non_zero_index_on_float_list(obj):
    obj.float_list[1] = 42.0
    assert obj.float_list[0] is None
    assert obj.float_list[1] == 42.0

def test_can_initialise_to_list(obj):
    obj.float_list = [0.0, 1.0, 2.0]
    assert obj.float_list[2] == 2.0

def test_raises_error_for_incorrect_type(obj):
    with pytest.raises(TypeError):
        obj.float_list[2] = 'hello'

def test_can_set_decorated_array(obj):
    obj.decorated_array[2] = 3.0
    assert obj._decorated_array == [None, None, 3.0]
    assert obj.decorated_array[0] is None
    assert obj.decorated_array[1] is None
    assert obj.decorated_array[2] == 3.0

def test_value_error_for_non_even_value_in_validated_array(obj):
    with pytest.raises(ValueError):
        obj.validated_array[0] = 1
    
def test_van_set_even_value_on_validated_array(obj):
    obj.validated_array[1] = 42
    assert obj.validated_array[1] == 42
    assert obj.validated_array[2] is None
