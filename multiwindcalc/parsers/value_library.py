"""A ValueLibrary interprets a value string (i.e. rhs of a key/value pair) and returns its substitute if the syntax refers to that library type"""


class ValueLibrary:
    def is_ref_to_this_library(self, value_string):
        return NotImplementedError()

    def create_value(self, value_string):
        return NotImplementedError()


class GeneratorLibrary(ValueLibrary):
    def __init__(self, generators):
        if not isinstance(generators, dict):
            raise TypeError('Generators library must take dict type')
        self._generators = generators

    def is_ref_to_this_library(self, value_string):
        return value_string.startswith('@') or value_string.startswith('gen:')

    def create_value(self, value_string):
        if value_string.startswith('@'):
            return self._generators[value_string[1:]].generate()
        elif value_string.startswith('gen:'):
            return self._generators[value_string[4:]].generate()
