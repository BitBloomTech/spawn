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

    Methods
    -------
    get()
        Gets the specification description as a dict
    """
    def get(self):
        """Gets the specification description

        Returns
        -------
        description: dict
            A dict representation of the description
        """
        raise NotImplementedError()


class SpecificationFileReader(SpecificationDescriptionProvider):
    """Implementation of ``SpecificationDescriptionProvider`` that reads
    the specification from a file

    Methods
    -------
    get()
        Gets the specification description
    """
    def __init__(self, input_file):
        """Initialises the ``SpecificationFileReader``

        Parameters
        ----------
        input_file : str
            The file containing the specification
        """
        validate_file(input_file, 'input_file')
        self._input_file = input_file

    def get(self):
        """Reads the specification description from a file

        Returns
        -------
        description: dict
            A dict representation of the description
        """
        with open(self._input_file) as input_fp:
            return load(input_fp)

class DictSpecificationProvider(SpecificationDescriptionProvider):
    """Class to provide a specification as a dict

    Methods
    ---------
    get()
        Gets the dict representation of the specification
    """
    def __init__(self, spec):
        """Initialises the ``DictSpecificationProvider

        Parameters
        ----------
        spec : dict
            The specification
        """
        validate_type(spec, dict, 'spec')
        self._spec = spec
    
    def get(self):
        """Gets the specification

        Returns
        description : dict
            A dict representation of the description
        """
        return self._spec

class SpecificationParser:
    """Class for parsing specifications

    Given a specification provider, the ``SpecificationParser`` will get the specification and
    produce a tree representation of the nodes.

    Methods
    -------
    parse()
        Parse the specification.
    """

    def __init__(self, provider):
        """Initialises the ``SpecificationParser``

        Parameters
        ----------
        provider : ``SpecificationDescriptionProvider``
            The source of the specification description
        """
        validate_type(provider, SpecificationDescriptionProvider, 'provider')
        self._provider = provider

    def parse(self):
        """Parse the specification description

        Reads the metadata from the file and creates any required value libraries,
        before initialising a ``SpecificationNodeParser`` to expand the nodes defined
        in the description.

        Returns
        -------
        spec : ``SpecificationModel``
            An object representing the expanded specification tree.
        """
        description = self._provider.get()
        metadata = SpecificationMetadata(description.get('creation_time'), description.get('notes'))
        value_libraries = self._get_value_libraries(description)
        node_parser = SpecificationNodeParser(value_libraries, self._get_combinators(), default_combinator=PRODUCT)
        root_node = node_parser.parse(description.get('spec'))
        return SpecificationModel(description.get('base_file'), root_node, metadata)

    @staticmethod
    def _get_value_libraries(description):
        generator_lib = GeneratorsParser().parse(description.get('generators'))
        macro_lib = {k: Macro(v) for k, v in description.get('macros', default={}).items()}
        return {
            GENERATOR: generator_lib,
            MACRO: macro_lib
        }

    @staticmethod
    def _get_combinators():
        return DEFAULT_COMBINATORS


class SpecificationNodeParser:
    """Expands the specification nodes, starting at the `node_spec` provided

    Given a starting `node_spec`, the specification `node_spec` parser assesses
    child nodes and expands them according to their values.

    Methods
    -------
    parse(node_spec, parent=None)
        Parse a `node_spec` and expand it's children.
    """

    def __init__(self, value_libraries=None, combinators=None, default_combinator=None):
        """Initialises the node parser

        Parameters
        ----------
        value_libraries : dict
            A mapping between value library names (e.g. generators, evaluators, macros)
            and value libraries.
            The default is {}
        combinators : dict
            A mapping between combinator names (e.g. zip, product) and combinators.
            The default is {}
        """
        self._value_libraries = value_libraries or {}
        self._combinators = combinators or {}
        self._default_combinator = default_combinator

    def parse(self, node_spec, parent=None):
        """Parse the `node_spec`, and expand its children.

        This iterates through a `node_spec` and expands it's children.

        Parameters
        ----------
        node_spec : dict
            A node specification
        parent : ``SpecificationNode``
            A specification node to add the new nodes to

        Returns
        -------
        node : ``SpecificationNode``
            The expanded `node_spec`
        """
        node_policies, node_spec = self._get_policies(node_spec)

        parent = parent or SpecificationNode.create_root(node_policies.pop(PATH, None))
        if node_spec is None or node_spec == {}:
            return parent

        validate_type(node_spec, dict, 'node_spec')

        (name, value), next_node_spec = self._get_next_node(node_spec)
        self._parse_value(parent, name, value, next_node_spec, node_policies)
        return parent

    def _parse_value(self, parent, name, value, next_node_spec, node_policies):
        # combinator lookup
        if self._is_combinator(name):
            self._parse_combinator(parent, name, value, next_node_spec, node_policies)
        # # list expansion
        elif isinstance(value, list):
            for val in value:
                self._parse_value(parent, name, val, next_node_spec, node_policies)
        # burrow into object
        elif isinstance(value, dict):
            self.parse(value, parent)
            self.parse(next_node_spec, parent)
        # rhs prefixed proxies (evaluators and co.) - short form and long form
        elif isinstance(value, str) and self._is_value_proxy(value):
            type_str, lookup_str = self._get_value_proxy(value)
            self._parse_value_proxy(next_node_spec, parent, name, type_str, lookup_str, node_policies)
        # simple single value
        else:
            next_parent = SpecificationNode(parent, name, value, node_policies.pop(PATH, None))
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

    def _parse_value_proxy(self, next_node_spec, parent, name, type_str, lookup_str, node_policies):
        if lookup_str not in self._value_libraries[type_str]:
            raise LookupError('Look-up string "{}" not found in "{}" library'.format(lookup_str, type_str))
        value = self._value_libraries[type_str][lookup_str].evaluate()
        self._parse_value(parent, name, value, next_node_spec, node_policies)

    def _get_combinator(self, name):
        prefix, combinator = self._parts(name)
        if prefix != COMBINATOR:
            #pylint: disable=line-too-long
            raise ValueError('prefix "{}" does not match combinator prefix "{}"'.format(prefix, COMBINATOR))
        if combinator not in self._combinators:
            raise ValueError('combinator "{}" not found'.format(f))
        return self._combinators[combinator]

    def _parse_combinator(self, parent, name, value, next_node_spec, node_policies):
        for node_spec in self._get_combinator(name)(value):
            self._parse_value(parent, None, node_spec, next_node_spec, node_policies)

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

    @staticmethod
    def _prefix(name):
        return '{}:'.format(name)

    @staticmethod
    def _parts(value):
        if ':' in value:
            return value.split(':', 1)
        return None, value
