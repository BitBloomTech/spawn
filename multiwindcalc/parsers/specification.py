from os import path
from json import load

from ..specification import SpecificationModel, SpecificationMetadata, SpecificationNode
from .generators import GeneratorsParser


_short_form_expansion = {
    '@': 'gen'
}


class SpecificationDescriptionProvider:
    def get(self):
        raise NotImplementedError()


class SpecificationFileReader(SpecificationDescriptionProvider):
    def __init__(self, input_file):
        if not path.isfile(input_file):
            raise FileNotFoundError('Could not find input file ' + input_file)
        self._input_file = input_file

    def get(self):
        with open(self._input_file) as input_fp:
            return load(input_fp)


class SpecificationParser:
    def __init__(self, provider):
        if not isinstance(provider, SpecificationDescriptionProvider):
            raise TypeError('provider must be of type ' + SpecificationDescriptionProvider)
        self._provider = provider

    def parse(self):
        description = self._provider.get()
        metadata = SpecificationMetadata(description.get('creation_time'), description.get('notes'))
        generator_lib = GeneratorsParser().parse(description.get('generators'))
        value_libraries = {
            'gen': generator_lib
        }
        root_node = SpecificationNodeParser(value_libraries).parse(description.get('spec'))
        return SpecificationModel(description.get('base_file'), root_node, metadata)


class SpecificationNodeParser:
    def __init__(self, value_libraries={}):
        self._value_libraries = value_libraries
        self._functions = {
            'zip': self._zip
        }

    def parse(self, node, parent=None):
        parent = parent or SpecificationNode.create_root()
        if node is None or node == {}:
            return parent
        if not isinstance(node, dict):
            raise TypeError('node must be of type dict')

        (name, value), next_node = self._get_next_node(node)
        self._parse_value(parent, name, value, next_node)
        return parent
    
    def _parse_value(self, parent, name, value, next_node):
        # function lookup
        if name in self._functions:
            for node in self._functions[name](value):
                self._parse_value(parent, None, node, next_node)
        # list expansion
        elif isinstance(value, list):
            for v in value:
                self._parse_value(parent, name, v, next_node)
        # burrow into object
        elif isinstance(value, dict):
            self.parse(value, parent)
            self.parse(next_node, parent)
        # rhs prefixed evaluation - short form and long form
        elif isinstance(value, str) and value[0] in _short_form_expansion:
            self._parse_evaluator(next_node, parent, name, _short_form_expansion[value[0]], value[1:])
        elif isinstance(value, str) and ':' in value:  # rhs prefixed evaluation
            parts = value.split(':')
            if parts[0] not in self._value_libraries:
                raise KeyError("Library identifier '{parts[0]}' not found when parsing RHS value string '{value}'")
            self._parse_evaluator(next_node, parent, name, parts[0], parts[1])
        # simple single value
        else:
            self.parse(next_node, SpecificationNode(parent, name, value))

    def _parse_evaluator(self, next_node, parent, name, type_str, lookup_str):
        if lookup_str not in self._value_libraries[type_str]:
            raise LookupError("Look-up string '{lookup_str}' not found in '{type_str}' library")
        self.parse(next_node, SpecificationNode(parent, name, self._value_libraries[type_str][lookup_str].evaluate()))

    @staticmethod
    def _zip(value):
        return [{k: v for k, v in zip(value.keys(), values)} for values in zip(*value.values())]

    @staticmethod
    def _get_next_node(node):
        next_key = list(node.keys())[0]
        return (next_key, node[next_key]), {k: v for k, v in node.items() if k != next_key}
