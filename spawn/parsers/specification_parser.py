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
"""This module defines the ``SpecificationParser``, which parsers specifications
"""
from json import load
from copy import deepcopy

from ..specification import (
    SpecificationModel, SpecificationMetadata, SpecificationNode,
    ValueProxyNode, SpecificationNodeFactory
)
from ..specification.combinators import zip_properties, product
from ..specification.evaluators import (
    RangeEvaluator, RepeatEvaluator, MultiplyEvaluator,
    DivideEvaluator, AddEvaluator, SubtractEvaluator
)
from .value_proxy import ValueProxyParser
from .generators import GeneratorsParser
from .macros import MacrosParser
from .constants import (
    COMBINATOR, ZIP, PRODUCT,
    RANGE, REPEAT, MULTIPLY, DIVIDE, ADD, SUBTRACT,
    PATH, POLICY, GHOST
)
from .value_libraries import ValueLibraries
from ..specification import generator_methods
from ..util.validation import validate_type, validate_file
from ..util.path_builder import PathBuilder

DEFAULT_COMBINATORS = {
    ZIP: zip_properties,
    PRODUCT: product
}

EVALUATOR_LIB = {
    RANGE: RangeEvaluator,
    REPEAT: RepeatEvaluator,
    MULTIPLY: MultiplyEvaluator,
    DIVIDE: DivideEvaluator,
    ADD: AddEvaluator,
    SUBTRACT: SubtractEvaluator
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
        self._spec = deepcopy(spec)

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

    def __init__(self, plugin_loader):
        """Initialises the :class:`SpecificationParser`

        :param provider: The source of the specification description
        :type provider: :class:`SpecificationDescriptionProvider`
        """
        self._plugin_loader = plugin_loader
        plugin_evaluators = self._plugin_loader.load_evaluators()
        self._pre_loaded_value_libraries = ValueLibraries(evaluators={**EVALUATOR_LIB, **plugin_evaluators})

    def parse(self, description):
        """Parse the specification description

        Reads the metadata from the file and creates any required value libraries,
        before initialising a :class:`SpecificationNodeParser` to expand the nodes defined
        in the description.

        :param description: The specification description
        :type description: dict

        :returns: An object representing the expanded specification tree.
        :rtype: :class:`SpecificationModel`
        """
        metadata = SpecificationMetadata(
            description.get('type'), description.get('creation_time'), description.get('notes')
        )
        value_libraries = self._pre_loaded_value_libraries.copy()
        value_proxy_parser = ValueProxyParser(value_libraries)
        self._update_value_libraries(description, value_proxy_parser, value_libraries)
        node_parser = SpecificationNodeParser(
            value_proxy_parser, self._get_combinators(), default_combinator=PRODUCT
        )
        root_node = node_parser.parse(description.get('spec'))
        root_node.evaluate()
        return SpecificationModel(description.get('base_file'), root_node, metadata)

    def _update_value_libraries(self, description, value_proxy_parser, value_libraries):
        built_in_generators = GeneratorsParser.load_generators_from_module(generator_methods)
        plugin_generators = self._plugin_loader.load_generators()
        generator_lib = GeneratorsParser({
            **built_in_generators, **plugin_generators
        }).parse(description.get('generators'))
        value_libraries.generators.update(generator_lib)
        macros_lib = MacrosParser(value_libraries, value_proxy_parser).parse(description.get('macros'))
        value_libraries.macros.update(macros_lib)

    @staticmethod
    def _get_combinators():
        return DEFAULT_COMBINATORS


class SpecificationNodeParser:
    """Expands the specification nodes, starting at the ``node_spec`` provided

    Given a starting `node_spec`, the specification ``node_spec`` parser assesses
    child nodes and expands them according to their values.
    """

    def __init__(self, value_proxy_parser, combinators=None, default_combinator=None):
        """Initialises the node parser

        :param value_proxy_parser: The value proxy parser
        :type value_proxy_parser: :class:`ValueProxyParser`
        :param combinators: A mapping between combinator names (e.g. zip, product) and combinators.
                           The default is {}
        :type combinators: dict
        """
        self._combinators = combinators or {}
        self._default_combinator = default_combinator
        self._node_factory = SpecificationNodeFactory()
        self._value_proxy_parser = value_proxy_parser

    def parse(self, node_spec, parent=None, node_policies=None, ghost_parameters=None):
        """Parse the `node_spec`, and expand its children.

        This iterates through a `node_spec` and expands it's children.

        :param node_spec: A node specification
        :type node_spec: dict
        :param parent: A specification node to add the new nodes to
        :type parent: :class:`SpecificationNode`

        :returns: The expanded `node_spec`
        :rtype: :class:`SpecificationNode`
        """
        next_node_policies, node_spec = self._get_policies(node_spec)
        node_policies = self._merge_policies(node_policies, next_node_policies)
        next_ghost_parameters, node_spec = self._get_ghost_parameters(node_spec)
        ghost_parameters = {**(ghost_parameters or {}), **next_ghost_parameters}

        parent = parent or SpecificationNode.create_root(node_policies.pop(PATH, None))
        if node_spec is None or node_spec == {}:
            return parent

        validate_type(node_spec, dict, 'node_spec')

        (name, value), next_node_spec = self._get_next_node(node_spec)
        self._parse_value(parent, name, value, next_node_spec, node_policies, ghost_parameters)
        return parent

    @staticmethod
    def _merge_policies(left, right):
        if not left:
            return right
        if not right:
            return left
        merged = {}
        if PATH in left and PATH in right:
            merged[PATH] = str(PathBuilder(left[PATH]).join(right[PATH]))
        return {**left, **right, **merged}

    def _parse_value(self, parent, name, value, next_node_spec, node_policies, ghost_parameters):
        # combinator lookup
        if self._is_combinator(name):
            self._parse_combinator(parent, name, value, next_node_spec, node_policies, ghost_parameters)
        # list expansion
        elif isinstance(value, list):
            for val in value:
                self._parse_value(parent, name, val, next_node_spec, node_policies, ghost_parameters)
        # burrow into object
        elif isinstance(value, dict):
            self.parse(value, parent, node_policies=node_policies, ghost_parameters=ghost_parameters)
            self.parse(next_node_spec, parent, node_policies=node_policies, ghost_parameters=ghost_parameters)
        # rhs prefixed proxies (evaluators and co.) - short form and long form
        elif isinstance(value, str) and self._is_value_proxy(value):
            next_parent = ValueProxyNode(
                parent, name, self._value_proxy_parser.parse(value),
                node_policies.get(PATH, None), ghost_parameters
            )
            self.parse(next_node_spec, next_parent)
        # simple single value
        else:
            next_parent = self._node_factory.create(
                parent, name, value, node_policies.get(PATH, None), ghost_parameters
            )
            self.parse(next_node_spec, next_parent)

    def _is_value_proxy(self, value):
        return self._value_proxy_parser.is_value_proxy(value)

    def _is_combinator(self, value):
        is_equal = lambda f: value == '{}{}'.format(self._prefix(COMBINATOR), f)
        return any(map(is_equal, self._combinators.keys()))

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
            self._parse_value(parent, '', node_spec, next_node_spec, node_policies, ghost_parameters)

    def _get_next_node(self, node_spec):
        next_key = list(node_spec.keys())[0]
        if len(node_spec) == 1:
            return (next_key, node_spec[next_key]), {}
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
