# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
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
"""Property class attributes to allow validation and type checking
"""
import re
import copy
import functools

from spawn.util.validation import validate_type

def typed_property(type_):
    """Function decorator for :class:`TypedProperty`
    """
    def _wrapper(fget):
        return TypedProperty(type_, fget)
    return _wrapper

def int_property(fget):
    """Function decorator for :class:`IntProperty`
    """
    return IntProperty(fget)

def float_property(fget):
    """Function decorator for :class:`FloatProperty`
    """
    return FloatProperty(fget)

def string_property(fget):
    """Function decorator for :class:`StringProperty`
    """
    return StringProperty(fget)

class PropertyBase:
    """Base class for properties
    """
    def __init__(
            self, type_, fget=None, fset=None, fdel=None, fvalidate=None,
            default=None, doc=None, abstract=False, readonly=False):
        """Initialises :class:`PropertyBase`

        :param fget: Getter function for property
        :type fget: func
        :param fset: Setter function for property
        :type fset: func
        :param fdel: Deleter function for property
        :type fdel: func
        :param fvalidate: Validation function for property
        :type fvalidate: func
        :param default: The default value for this property
        :type default: object
        :parm doc: The docstring for this property
        :type doc: str
        :param abstract: ``True`` if this property is abstract (requires implementation);
        ``False`` otherwise.
        :type abstract: bool
        """
        self._type = type_
        self._fget = fget
        self._fset = fset
        self._fdel = fdel
        self._fvalidate = fvalidate
        self._default = default
        self.__doc__ = doc if doc is not None else fget.__doc__ if fget is not None else None
        self._name = None
        self._abstract = abstract
        self._readonly = readonly

    def __set_name__(self, _obj, name):
        self._name = name

    @property
    def type(self):
        """The type of this property

        :returns: The type
        :rtype: type
        """
        return self._type


    def getter(self, fget):
        """Acts as a function decorator to provide a :class:`TypedProperty` with a getter

        :param fget: The getter function
        :type fget: func
        """
        if self._fget is not None:
            raise ValueError('Cannot set fget more than once')
        other = copy.copy(self)
        #pylint: disable=protected-access
        other._fget = fget
        return other

    def setter(self, fset):
        """Acts as a function decorator to provide a :class:`TypedProperty` with a setter

        :param fset: The setter function
        :type fset: func
        """
        if self._fset is not None:
            raise ValueError('Cannot set fset more than once')
        if self._fget is None:
            raise ValueError('Must set getter before setting fset')
        other = copy.copy(self)
        #pylint: disable=protected-access
        other._fset = fset
        return other

    def deleter(self, fdel):
        """Acts as a function decorator to provide a :class:`TypedProperty` with a deleter

        :param fdel: The deleter function
        :type fdel: func
        """
        if self._fdel is not None:
            raise ValueError('Cannot set fdel more than once')
        if self._fget is None or self._fset is None:
            raise ValueError('Must set getter and setter before setting fdel')
        other = copy.copy(self)
        #pylint: disable=protected-access
        other._fdel = fdel
        return other

    def validator(self, fvalidate):
        """Acts as a function decorator to provide a :class:`TypedProperty` with a validator

        :param fvalidate: The validator function
        :type fvalidate: func
        """
        other = copy.copy(self)
        #pylint: disable=protected-access
        other._fvalidate = fvalidate
        return other

    def _get_fname(self, function):
        return '{}_{}'.format(function, self._name)

    def __call__(self, fget):
        return self.getter(fget)

class TypedProperty(PropertyBase):
    """Base class for typed properties
    """
    def __get__(self, obj, _type=None):
        if obj is None:
            return self
        if self._name is None:
            raise ValueError('Cannot get property, name has not been set')
        if hasattr(obj, self._get_fname('get')):
            return getattr(obj, self._get_fname('get'))()
        if self._fget:
            return self._fget(obj)
        if self._abstract:
            raise NotImplementedError()
        return obj.__dict__.get(self._name, self._default)

    def __set__(self, obj, value):
        if obj is None:
            return
        if self._name is None:
            raise ValueError('Cannot set property, name has not been set')
        if self._readonly:
            raise NotImplementedError()
        self._validate(obj, value)
        if hasattr(obj, self._get_fname('validate')):
            getattr(obj, self._get_fname('validate'))(value)
        elif self._fvalidate:
            self._fvalidate(obj, value)
        if hasattr(obj, self._get_fname('set')):
            getattr(obj, self._get_fname('set'))(value)
        elif self._fset:
            self._fset(obj, value)
        elif self._abstract:
            raise NotImplementedError()
        else:
            obj.__dict__[self._name] = value

    def __delete__(self, obj):
        if self._name is None:
            raise ValueError('Cannot delete property, name has not been set')
        if hasattr(obj, self._get_fname('delete')):
            getattr(obj, self._get_fname('delete'))()
        elif self._fdel:
            self._fdel(obj)
        elif self._abstract:
            raise NotImplementedError()
        else:
            del obj.__dict__[self._name]

    def _validate(self, _obj, value):
        if not isinstance(value, self._type):
            raise TypeError('value')

class NumericProperty(TypedProperty):
    """Implementation of :class:`TypedProperty` for numeric (int or float) properties

    Adds min and max options
    """
    #pylint: disable=redefined-builtin
    def __init__(
            self, type_, fget=None, fset=None, fdel=None, fvalidate=None,
            default=None, doc=None, abstract=False, readonly=False,
            min=None, max=None):
        """Initialises :class:`NumericProperty`

        :param fget: Getter function for property
        :type fget: func
        :param fset: Setter function for property
        :type fset: func
        :param fdel: Deleter function for property
        :type fdel: func
        :param fvalidate: Validation function for property
        :type fvalidate: func
        :param default: The default value for this property
        :type default: numeric
        :parm doc: The docstring for this property
        :type doc: str
        :param abstract: ``True`` if this property is abstract (requires implementation);
        ``False`` otherwise.
        :type abstract: bool
        :param min: Minimum allowed value for this property
        :type min: numeric
        :param max: Maximum allowed value for this property
        :type max: numeric
        """
        super().__init__(type_, fget, fset, fdel, fvalidate, default, doc, abstract, readonly)
        if min is not None and not isinstance(min, type_):
            raise TypeError('min')
        if max is not None and not isinstance(max, type_):
            raise TypeError('max')
        self._min = min
        self._max = max

    def _validate(self, obj, value):
        super()._validate(obj, value)
        if self._min is not None and value < self._min:
            raise ValueError('{} < {}'.format(value, self._min))
        if self._max is not None and value > self._max:
            raise ValueError('{} > {}'.format(value, self._max))

class IntProperty(NumericProperty):
    """Implementation of :class:`NumericProperty` for int properties
    """
    #pylint: disable=redefined-builtin
    def __init__(
            self, fget=None, fset=None, fdel=None, fvalidate=None,
            default=None, doc=None, abstract=False, readonly=False,
            min=None, max=None):
        """Initialises :class:`IntProperty`

        :param fget: Getter function for property
        :type fget: func
        :param fset: Setter function for property
        :type fset: func
        :param fdel: Deleter function for property
        :type fdel: func
        :param fvalidate: Validation function for property
        :type fvalidate: func
        :param default: The default value for this property
        :type default: int
        :parm doc: The docstring for this property
        :type doc: str
        :param abstract: ``True`` if this property is abstract (requires implementation);
        ``False`` otherwise.
        :type abstract: bool
        :param min: Minimum allowed value for this property
        :type min: int
        :param max: Maximum allowed value for this property
        :type max: int
        """
        super().__init__(
            int, fget, fset, fdel, fvalidate, default, doc, abstract, readonly, min, max
        )

class FloatProperty(NumericProperty):
    """Implementation of :class:`NumericProperty` for float properties
    """
    #pylint: disable=redefined-builtin
    def __init__(
            self, fget=None, fset=None, fdel=None, fvalidate=None,
            default=None, doc=None, abstract=False, readonly=False,
            min=None, max=None):
        """Initialises :class:`FloatProperty`

        :param fget: Getter function for property
        :type fget: func
        :param fset: Setter function for property
        :type fset: func
        :param fdel: Deleter function for property
        :type fdel: func
        :param fvalidate: Validation function for property
        :type fvalidate: func
        :param default: The default value for this property
        :type default: float
        :parm doc: The docstring for this property
        :type doc: str
        :param abstract: ``True`` if this property is abstract (requires implementation);
        ``False`` otherwise.
        :type abstract: bool
        :param min: Minimum allowed value for this property
        :type min: float
        :param max: Maximum allowed value for this property
        :type max: float
        """
        super().__init__(
            float, fget, fset, fdel, fvalidate, default, doc, abstract, readonly, min, max
        )

class StringProperty(TypedProperty):
    """Implementation of :class:`TypedProperty` for string properties
    """
    def __init__(
            self, fget=None, fset=None, fdel=None, fvalidate=None,
            default=None, doc=None, abstract=False, readonly=False,
            possible_values=None, regex=None):
        """Initialises :class:`StringProperty`

        :param fget: Getter function for property
        :type fget: func
        :param fset: Setter function for property
        :type fset: func
        :param fdel: Deleter function for property
        :type fdel: func
        :param fvalidate: Validation function for property
        :type fvalidate: func
        :param default: The default value for this property
        :type default: str
        :parm doc: The docstring for this property
        :type doc: str
        :param abstract: ``True`` if this property is abstract (requires implementation);
        ``False`` otherwise.
        :type abstract: bool
        :param possible_values: Array of possible values for this property
        :type possible_values: list
        :param regex: Regex that this property must match
        :type regex: str
        """
        super().__init__(str, fget, fset, fdel, fvalidate, default, doc, abstract, readonly)
        self._possible_values = possible_values
        self._regex = regex

    def _validate(self, obj, value):
        super()._validate(obj, value)
        if self._possible_values is not None and value not in self._possible_values:
            raise ValueError('"{}" not in {}'.format(value, self._possible_values))
        if self._regex is not None and not re.search(self._regex, value):
            raise ValueError('"{}" does not match pattern "{}"'.format(value, self._regex))

class ArrayProperty(PropertyBase):
    """Implementation of :class:`PropertyBase` for array properties
    :meth:`__get__`, :meth:`__set__` and :meth:`__delete__` return array wrappers
    that allow indexes to be used
    """
    def __init__(
            self, type_, fget=None, fset=None, fdel=None, fvalidate=None,
            default=None, doc=None, abstract=False, readonly=False):
        """Initialises :class:`ArrayProperty`

        :param fget: Getter function for property
        :type fget: func
        :param fset: Setter function for property
        :type fset: func
        :param fdel: Deleter function for property
        :type fdel: func
        :param fvalidate: Validation function for property
        :type fvalidate: func
        :param default: The default value for this property
        :type default: object
        :parm doc: The docstring for this property
        :type doc: str
        :param abstract: ``True`` if this property is abstract (requires implementation);
        ``False`` otherwise.
        :type abstract: bool
        """
        super().__init__(fget, fset, fdel, fvalidate, default, doc, abstract, readonly)
        self._type = type_

    def __get__(self, obj, _type=None):
        if obj is None:
            return self
        if self._name is None:
            raise ValueError('Cannot get property, name has not been set')
        if self._abstract:
            raise NotImplementedError()
        return self._wrapper(obj)

    def __set__(self, obj, value):
        if obj is None:
            return
        if self._name is None:
            raise ValueError('Cannot set property, name has not been set')
        if self._readonly or self._abstract:
            raise NotImplementedError()
        validate_type(value, list, 'value')
        wrapper = self._wrapper(obj)
        for i, v in enumerate(value):
            wrapper[i] = v

    def __delete__(self, obj):
        if self._name is None:
            raise ValueError('Cannot delete property, name has not been set')
        if hasattr(obj, self._get_fname('delete')):
            getattr(obj, self._get_fname('delete'))()
        if self._abstract:
            raise NotImplementedError()
        if self._fget or self._fset or self._fdel:
            raise ValueError('Cannot delete array with custom getters and setters')
        del obj.__dict__[self._name]

    def _wrapper(self, obj):
        fget = functools.partial(self._fget, obj) if self._fget else self._get_method(obj, 'get')
        fset = functools.partial(self._fset, obj) if self._fset else self._get_method(obj, 'set')
        fdel = functools.partial(self._fdel, obj) if self._fdel else self._get_method(obj, 'delete')
        fvalidate = (
            functools.partial(self._fvalidate, obj) if self._fvalidate
            else self._get_method(obj, 'validate')
        )
        obj.__dict__.setdefault(self._name, [])
        return ArrayWrapper(self._type, fget, fset, fdel, fvalidate, obj.__dict__[self._name])

    def _get_method(self, obj, name):
        if hasattr(obj, self._get_fname(name)):
            return getattr(obj, self._get_fname(name))
        return None

class ArrayWrapper:
    """Wrapper for arrays that allows custom getters, setters, deleters and validators to be used
    """
    def __init__(self, type_, fget=None, fset=None, fdel=None, fvalidate=None, store=None):
        """Initialises :class:`ArrayWrapper`

        :param type_: The type of array
        :type type_: type
        :param fget: The getter for the array
        :type fget: func
        :param fset: The setter for the array
        :type fset: func
        :param fdel: The deleter for the array
        :type fdel: func
        :param fvalidate: The validator for the array
        :type fvalidate: func
        :param store: The store for the array
        :type store: list
        """
        validate_type(store, list, 'store')
        self._type = type_
        self._fget = fget
        self._fset = fset
        self._fdel = fdel
        self._fvalidate = fvalidate
        self._store = store

    def __getitem__(self, index):
        validate_type(index, int, 'index')
        if self._fget:
            return self._fget(index)
        if self._store is not None:
            self._extend(index + 1)
            return self._store[index]
        raise ValueError('Could not get value for property, no store and no getter specified')

    def __setitem__(self, index, value):
        validate_type(index, int, 'index')
        validate_type(value, self._type, 'value')
        if self._fvalidate:
            self._fvalidate(index, value)
        if self._fset:
            self._fset(index, value)
        elif self._store is not None:
            self._extend(index + 1)
            self._store[index] = value
        else:
            raise ValueError('Could not set value for property, no store and no setter specified')

    def __delitem__(self, index):
        validate_type(index, int, 'index')
        if self._fdel:
            self._fdel(index)
        elif self._store is not None:
            self._extend(index + 1)
            del self._store[index]
        else:
            raise ValueError(
                'Could not deleted index for property, no store and no setter specified'
            )

    def _extend(self, length):
        if self._store is None:
            raise ValueError('store not defined for array')
        while len(self._store) < length:
            self._store.append(None)
