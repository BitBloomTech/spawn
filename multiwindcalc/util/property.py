import re
import copy

def typed_property(type_):
    def _wrapper(fget):
        return TypedProperty(type_, fget)
    return _wrapper

def int_property(fget):
    return IntProperty(fget)

def float_property(fget):
    return FloatProperty(fget)

def string_property(fget):
    return StringProperty(fget)

class TypedProperty:
    def __init__(self, type_, fget=None, fset=None, fdel=None, fvalidate=None, default=None, docs=None):
        self._type = type_
        self._fget = fget
        self._fset = fset
        self._fdel = fdel
        self._fvalidate = fvalidate
        self._default = default
        self.__doc__ = docs if docs is not None else fget.__doc__ if fget is not None else None
        self._name = None

    def __set_name__(self, _obj, name):
        self._name = name

    def __get__(self, obj, _type=None):
        if obj is None:
            return self
        if self._name is None:
            raise ValueError('Cannot get property, name has not been set')
        if hasattr(obj, self._get_fname('get')):
            return getattr(obj, self._get_fname('get'))()
        if self._fget:
            return self._fget(obj)
        return obj.__dict__.get(self._name, self._default)
    
    def __set__(self, obj, value):
        if obj is None:
            return
        if self._name is None:
            raise ValueError('Cannot set property, name has not been set')
        self._validate(obj, value)
        if hasattr(obj, self._get_fname('validate')):
            getattr(obj, self._get_fname('validate'))(value)
        elif self._fvalidate:
            self._fvalidate(obj, value)
        if hasattr(obj, self._get_fname('set')):
            getattr(obj, self._get_fname('set'))(value)
        elif self._fset:
            self._fset(obj, value)
        else:
            obj.__dict__[self._name] = value
    
    def __delete__(self, obj):
        if self._name is None:
            raise ValueError('Cannot delete property, name has not been set')
        if hasattr(obj, self._get_fname('delete')):
            getattr(obj, self._get_fname('delete'))()
        elif self._fdel:
            self._fdel(obj)
        else:
            del obj.__dict__[self._name]
    
    def _validate(self, obj, value):
        if not isinstance(value, self._type):
            raise TypeError('value')
    
    def getter(self, fget):
        if self._fget is not None:
            raise ValueError('Cannot set fget more than once')
        other = copy.copy(self)
        other._fget = fget
        return other
    
    def setter(self, fset):
        if self._fset is not None:
            raise ValueError('Cannot set fset more than once')
        if self._fget is None:
            raise ValueError('Must set getter before setting fset')
        other = copy.copy(self)
        other._fset = fset
        return other
    
    def deleter(self, fdel):
        if self._fdel is not None:
            raise ValueError('Cannot set fdel more than once')
        if self._fget is None or self._fset is None:
            raise ValueError('Must set getter and setter before setting fdel')
        other = copy.copy(self)
        other._fdel = fdel
        return other
    
    def validator(self, fvalidate):
        other = copy.copy(self)
        other._fvalidate = fvalidate
        return other
    
    def _get_fname(self, function):
        return '{}_{}'.format(function, self._name)

class NumericProperty(TypedProperty):
    def __init__(self, type_, fget=None, fset=None, fdel=None, fvalidate=None, default=None, docs=None, min=None, max=None):
        super(NumericProperty, self).__init__(type_, fget, fset, fdel, fvalidate, default, docs)
        if min is not None and not isinstance(min, type_):
            raise TypeError('min')
        if max is not None and not isinstance(max, type_):
            raise TypeError('max')
        self._min = min
        self._max = max
    
    def _validate(self, obj, value):
        super(NumericProperty, self)._validate(obj, value)
        if self._min is not None and value < self._min:
            raise ValueError('{} < {}'.format(value, self._min))
        if self._max is not None and value > self._max:
            raise ValueError('{} > {}'.format(value, self._max))

class IntProperty(NumericProperty):
    def __init__(self, fget=None, fset=None, fdel=None, fvalidate=None, default=None, docs=None, min=None, max=None):
        super(IntProperty, self).__init__(int, fget, fset, fdel, fvalidate, default, docs, min, max)

class FloatProperty(NumericProperty):
    def __init__(self, fget=None, fset=None, fdel=None, fvalidate=None, default=None, docs=None, min=None, max=None):
        super(FloatProperty, self).__init__(float, fget, fset, fdel, fvalidate, default, docs, min, max)

class StringProperty(TypedProperty):
    def __init__(self, fget=None, fset=None, fdel=None, fvalidate=None, default=None, docs=None, possible_values=None, regex=None):
        super(StringProperty, self).__init__(str, fget, fset, fdel, fvalidate, default, docs)
        self._possible_values = possible_values
        self._regex = regex
    
    def _validate(self, obj, value):
        super(StringProperty, self)._validate(obj, value)
        if self._possible_values is not None and value not in self._possible_values:
            raise ValueError('"{}" not in {}'.format(value, self._possible_values))
        if self._regex is not None and not re.search(self._regex, value):
            raise ValueError('"{}" does not match pattern "{}"'.format(value, self._regex))
