from os import path
from json import load

from ..specification import SpecificationModel, SpecificationMetadata, SpecificationNode

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
        root_node = SpecificationNodeParser().parse(description.get('spec'))
        return SpecificationModel(description.get('base_file'), root_node, metadata)

class SpecificationNodeParser:
    def __init__(self):
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
        if name in self._functions:
            for node in self._functions[name](value):
                self._parse_value(parent, None, node, next_node)
        elif isinstance(value, list):
            for v in value:
                self._parse_value(parent, name, v, next_node)
        elif isinstance(value, dict):
            self.parse(value, parent)
            self.parse(next_node, parent)
        else:
            self.parse(next_node, SpecificationNode(parent, name, value))
    
    def _zip(self, value):
        return [{k: v for k, v in zip(value.keys(), values)} for values in zip(*value.values())]

    def _get_next_node(self, node):
        next_key = list(node.keys())[0]
        return (next_key, node[next_key]), {k: v for k, v in node.items() if k != next_key}
