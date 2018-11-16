"""This module defines the ``SpecificationParser``, which parsers specifications
"""
from os import path
from json import load

from ..specification import SpecificationModel, SpecificationMetadata, SpecificationNode
from ..specification import Macro
from ..specification.combinators import zip_properties, product
from .generators import GeneratorsParser
from ..util.validation import validate_type, validate_file

COMBINATOR = 'combine'
GENERATOR = 'gen'
MACRO = 'macro'
ZIP = 'zip'
PRODUCT = 'product'
POLICY = 'policy'
PATH = 'path'
GHOST = '_'

SHORT_FORM_EXPANSION = {
    '@': GENERATOR,
    '$': MACRO
}

DEFAULT_COMBINATORS = {
    ZIP: zip_properties,
    PRODUCT: product
}

class SpecificationDescriptionProvider:
    """Abstract base class for implementations that provide the specification description.
    """
    def get(self):
        """Gets the specification description

        :returns: A dict representation of the description
        :rtype: dict
        """
        raise NotImplementedError()


class SpecificationFileReader(SpecificationDescriptionProvider):
    """Implementation of :class:`SpecificationDescriptionProvider` that reads
    the specification from a file
    """
    def __init__(self, input_file):
        """Initialises the :class:`SpecificationFileReader`

        :param input_file: The input file
        :type input_file: path-like
        """
        validate_file(input_file, 'input_file')
        self._input_file = input_file

    def get(self):
        """Reads the specification description from a file

        :returns: A dict representation of the description
        :rtype: dict
        """
        with open(self._input_file) as input_fp:
            return load(input_fp)

class DictSpecificationProvider(SpecificationDescriptionProvider):
    """Implementation of :class:`SpecificationDescriptionProvider` that reads
    the specification from a provided dict
    """
    def __init__(self, spec):
        """Initialises the :class:`DictSpecificationProvider`

        :param spec: The specification
        :type spec: dict
        """
        validate_type(spec, dict, 'spec')
        self._spec = spec
    
    def get(self):
        """Gets the specification

        :returns: A dict representation of the description
        :rtype: dict
        """
        return self._spec

class SpecificationParser:
    """Class for parsing specifications

    Given a specification provider, the :class:`SpecificationParser` will get the specification and
    produce a tree representation of the nodes.
    """

    def __init__(self, provider):
        """Initialises the :class:`SpecificationParser`

        :param provider: The source of the specification description
        :type provider: :class:`SpecificationDescriptionProvider`
        """
        validate_type(provider, SpecificationDescriptionProvider, 'provider')
        self._provider = provider

    def parse(self):
        """Parse the specification description

        Reads the metadata from the file and creates any required value libraries,
        before initialising a :class:`SpecificationNodeParser` to expand the nodes defined
        in the description.

        :returns: An object representing the expanded specification tree.
        :rtype: :class:`SpecificationModel`
        """
        description = self._provider.get()
        metadata = SpecificationMetadata(description.get('type'), description.get('creation_time'), description.get('notes'))
        value_libraries = self._get_value_libraries(description)
        node_parser = SpecificationNodeParser(value_libraries, self._get_combinators(), default_combinator=PRODUCT)
        root_node = node_parser.parse(description.get('spec'))
        return SpecificationModel(description.get('base_file'), root_node, metadata)

    @staticmethod
    def _get_value_libraries(description):
        generator_lib = GeneratorsParser().parse(description.get('generators'))
        macro_lib = {k: Macro(v) for k, v in description.get('macros', {}).items()}
        return {
            GENERATOR: generator_lib,
            MACRO: macro_lib
        }

    @staticmethod
    def _get_combinators():
        return DEFAULT_COMBINATORS


class SpecificationNodeParser:
    """Expands the specification nodes, starting at the ``node_spec`` provided

    Given a starting `node_spec`, the specification ``node_spec`` parser assesses
    child nodes and expands them according to their values.
    """

    def __init__(self, value_libraries=None, combinators=None, default_combinator=None):
        """Initialises the node parser

        :param value_libraries: A mapping between value library names (e.g. generators, evaluators, macros)
                                and value libraries.
                                The default is {}.
        :type value_libraries: dict
        :param combinators: A mapping between combinator names (e.g. zip, product) and combinators.
                           The default is {}
        :type combinators: dict
        """
        self._value_libraries = value_libraries or {}
        self._combinators = combinators or {}
        self._default_combinator = default_combinator

    def parse(self, node_spec, parent=None):
        """Parse the `node_spec`, and expand its children.

        This iterates through a `node_spec` and expands it's children.

        :param node_spec: A node specification
        :type node_spec: dict
        :param parent: A specification node to add the new nodes to
        :type parent: :class:`SpecificationNode`

        :returns: The expanded `node_spec`
        :rtype: :class:`SpecificationNode`
        """
        node_policies, node_spec = self._get_policies(node_spec)
        ghost_parameters, node_spec = self._get_ghost_parameters(node_spec)

        parent = parent or SpecificationNode.create_root(node_policies.pop(PATH, None))
        if node_spec is None or node_spec == {}:
            return parent

        validate_type(node_spec, dict, 'node_spec')

        (name, value), next_node_spec = self._get_next_node(node_spec)
        self._parse_value(parent, name, value, next_node_spec, node_policies, ghost_parameters)
        return parent

    def _parse_value(self, parent, name, value, next_node_spec, node_policies, ghost_parameters):
        # combinator lookup
        if self._is_combinator(name):
            self._parse_combinator(parent, name, value, next_node_spec, node_policies, ghost_parameters)
        # # list expansion
        elif isinstance(value, list):
            for val in value:
                self._parse_value(parent, name, val, next_node_spec, node_policies, ghost_parameters)
        # burrow into object
        elif isinstance(value, dict):
            self.parse(value, parent)
            self.parse(next_node_spec, parent)
        # rhs prefixed proxies (evaluators and co.) - short form and long form
        elif isinstance(value, str) and self._is_value_proxy(value):
            type_str, lookup_str = self._get_value_proxy(value)
            self._parse_value_proxy(next_node_spec, parent, name, type_str, lookup_str, node_policies, ghost_parameters)
        # simple single value
        else:
            next_parent = SpecificationNode(parent, name, value, node_policies.pop(PATH, None), ghost_parameters)
            self.parse(next_node_spec, next_parent)

    def _is_value_proxy(self, value):
        if value[0] in SHORT_FORM_EXPANSION:
            prefix = SHORT_FORM_EXPANSION[value[0]]
        else:
            prefix, _ = self._parts(value)
        return prefix in self._value_libraries

    def _is_combinator(self, value):
        is_equal = lambda f: value == '{}{}'.format(self._prefix(COMBINATOR), f)
        return any(map(is_equal, self._combinators.keys()))

    def _get_value_proxy(self, value_str):
        if value_str[0] in SHORT_FORM_EXPANSION:
            return SHORT_FORM_EXPANSION[value_str[0]], value_str[1:]
        lib, name = self._parts(value_str)
        if lib not in self._value_libraries:
            #pylint:disable=line-too-long
            raise KeyError('Library identifier "{}" not found when parsing RHS value string "{}"'.format(lib, value_str))
        return lib, name

    def _parse_value_proxy(self, next_node_spec, parent, name, type_str, lookup_str, node_policies, ghost_parameters):
        if lookup_str not in self._value_libraries[type_str]:
            raise LookupError('Look-up string "{}" not found in "{}" library'.format(lookup_str, type_str))
        value = self._value_libraries[type_str][lookup_str].evaluate()
        self._parse_value(parent, name, value, next_node_spec, node_policies, ghost_parameters)

    def _get_combinator(self, name):
        prefix, combinator = self._parts(name)
        if prefix != COMBINATOR:
            #pylint: disable=line-too-long
            raise ValueError('prefix "{}" does not match combinator prefix "{}"'.format(prefix, COMBINATOR))
        if combinator not in self._combinators:
            raise ValueError('combinator "{}" not found'.format(combinator))
        return self._combinators[combinator]

    def _parse_combinator(self, parent, name, value, next_node_spec, node_policies, ghost_parameters):
        for node_spec in self._get_combinator(name)(value):
            self._parse_value(parent, None, node_spec, next_node_spec, node_policies, ghost_parameters)

    def _get_next_node(self, node_spec):
        next_key = list(node_spec.keys())[0]
        # If the next value is a list, expand it using the default combinator if possible
        if not self._is_combinator(next_key) and isinstance(node_spec[next_key], list) and self._default_combinator:
            return ('{}{}'.format(self._prefix(COMBINATOR), self._default_combinator), node_spec), {}
        next_node_spec = {k: v for k, v in node_spec.items() if k != next_key}
        return (next_key, node_spec[next_key]), next_node_spec

    def _get_policies(self, node_spec):
        if not node_spec:
            return {}, {}
        prefix = self._prefix(POLICY)
        policies = {k.replace(prefix, ''): v for k, v in node_spec.items() if k.startswith(prefix)}
        return policies, {k: v for k, v in node_spec.items() if not k.startswith(prefix)}
    
    def _get_ghost_parameters(self, node_spec):
        if not node_spec:
            return {}, {}
        ghost_parameters = {self._deghost(k): v for k, v in node_spec.items() if self._is_ghost(k)}
        return ghost_parameters, {k: v for k, v in node_spec.items() if not self._is_ghost(k)}
    
    @staticmethod
    def _is_ghost(prop):
        return prop.startswith(GHOST)

    @staticmethod
    def _deghost(prop):
        if not SpecificationNodeParser._is_ghost(prop):
            raise ValueError('Cannot deghost a non-ghost property')
        return prop[1:]

    @staticmethod
    def _prefix(name):
        return '{}:'.format(name)

    @staticmethod
    def _parts(value):
        if ':' in value:
            return value.split(':', 1)
        return None, value
