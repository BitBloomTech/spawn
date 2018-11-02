"""Property class attributes to allow validation and type checking
"""
import re
import copy

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

class TypedProperty:
    """Base class for typed properties
    """
    def __init__(self, type_, fget=None, fset=None, fdel=None, fvalidate=None, default=None, doc=None, abstract=False, readonly=False):
        """Initialises :class:`TypedProperty`

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
        :param abstract: ``True`` if this property is abstract (requires implementation); ``False`` otherwise.
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
    
    @property
    def type(self):
        """The type of this property
        
        :returns: The type
        :rtype: type
        """
        return self._type

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
    
    def _validate(self, obj, value):
        if not isinstance(value, self._type):
            raise TypeError('value')
    
    def getter(self, fget):
        """Acts as a function decorator to provide a :class:`TypedProperty` with a getter

        :param fget: The getter function
        :type fget: func
        """
        if self._fget is not None:
            raise ValueError('Cannot set fget more than once')
        other = copy.copy(self)
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
        other._fdel = fdel
        return other
    
    def validator(self, fvalidate):
        """Acts as a function decorator to provide a :class:`TypedProperty` with a validator

        :param fvalidate: The validator function
        :type fvalidate: func
        """
        other = copy.copy(self)
        other._fvalidate = fvalidate
        return other
    
    def _get_fname(self, function):
        return '{}_{}'.format(function, self._name)

    def __call__(self, fget):
        return self.getter(fget)

class NumericProperty(TypedProperty):
    """Implementation of :class:`TypedProperty` for numeric (int or float) properties

    Adds min and max options
    """
    def __init__(self, type_, fget=None, fset=None, fdel=None, fvalidate=None, default=None, doc=None, abstract=False, readonly=False, min=None, max=None):
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
        :param abstract: ``True`` if this property is abstract (requires implementation); ``False`` otherwise.
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
    def __init__(self, fget=None, fset=None, fdel=None, fvalidate=None, default=None, doc=None, abstract=False, readonly=False, min=None, max=None):
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
        :param abstract: ``True`` if this property is abstract (requires implementation); ``False`` otherwise.
        :type abstract: bool
        :param min: Minimum allowed value for this property
        :type min: int
        :param max: Maximum allowed value for this property
        :type max: int
        """
        super().__init__(int, fget, fset, fdel, fvalidate, default, doc, abstract, readonly, min, max)

class FloatProperty(NumericProperty):
    """Implementation of :class:`NumericProperty` for float properties
    """
    def __init__(self, fget=None, fset=None, fdel=None, fvalidate=None, default=None, doc=None, abstract=False, readonly=False, min=None, max=None):
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
        :param abstract: ``True`` if this property is abstract (requires implementation); ``False`` otherwise.
        :type abstract: bool
        :param min: Minimum allowed value for this property
        :type min: float
        :param max: Maximum allowed value for this property
        :type max: float
        """
        super().__init__(float, fget, fset, fdel, fvalidate, default, doc, abstract, readonly, min, max)

class StringProperty(TypedProperty):
    """Implementation of :class:`TypedProperty` for string properties
    """
    def __init__(self, fget=None, fset=None, fdel=None, fvalidate=None, default=None, doc=None, abstract=False, readonly=False, possible_values=None, regex=None):
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
        :param abstract: ``True`` if this property is abstract (requires implementation); ``False`` otherwise.
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
