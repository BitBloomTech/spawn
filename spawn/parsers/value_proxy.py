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
"""Implements the evaluators parser
"""

import ast

from spawn.specification.evaluators import ParameterEvaluator

from .constants import (
    MACRO, GENERATOR, EVALUATOR, PARAMETER,
    MULTIPLY, DIVIDE, ADD, SUBTRACT,
    SHORT_FORM_EXPANSION
)

OP_NAMES = {
    ast.Mult: MULTIPLY,
    ast.Div: DIVIDE,
    ast.Add: ADD,
    ast.Sub: SUBTRACT
}

MACRO_TOKEN = '__macro__'
GENERATOR_TOKEN = '__generator__'
PARAMETER_TOKEN = '__param__'
EVALUATOR_TOKEN = ''

TOKENS = {
    MACRO: MACRO_TOKEN,
    GENERATOR: GENERATOR_TOKEN,
    PARAMETER: PARAMETER_TOKEN,
    EVALUATOR: EVALUATOR_TOKEN
}

class ValueProxyVisitor(ast.NodeVisitor):
    """Implementation of :class:`ast.NodeVisitor` that is able to parse evaluators
    """
    def __init__(self, evaluator_library, macro_library, generator_library, value_proxy_string):
        """Initialises :class:`EvaluatorVisitor`

        :param evaluator_library: The evaluator library
        :type evaluator_library: dict
        :param macro_library: The macro library
        :type macro_library: dict
        :param generator_library: The generator library
        :type generator_library: dict
        :param value_proxy_string: The string to be evaluated
        :type value_proxy_string: str
        """
        self._evaluator_library = evaluator_library
        self._macro_library = macro_library
        self._generator_library = generator_library
        self._value_proxy_string = value_proxy_string
        self._value_proxy = None

    #pylint: disable=invalid-name
    def visit_Call(self, node):
        """Parse :class:`ast.Call` nodes

        Recursively calls :method:`visit` on args

        :param node: The node to parse
        :type node: :class:`ast.Call`

        :returns: A value proxy parsed from the node
        :rtype: :class:`ValueProxy`
        """
        arg_values = [self.visit(a) for a in node.args]
        if any(a is None for a in arg_values):
            null_arg_index = arg_values.index(None)
            offset = node.args[null_arg_index].col_offset
            raise SyntaxError('Invalid syntax in {} at position {}'.format(self._value_proxy_string, offset))
        if node.func.id not in self._evaluator_library:
            raise LookupError('Evaluator {} not found'.format(node.func.id))
        self._value_proxy = self._evaluator_library[node.func.id](*arg_values)
        return self._value_proxy

    #pylint: disable=invalid-name,no-self-use
    def visit_Num(self, node):
        """Parse :class:`ast.Num` nodes

        Returns the value at the node

        :param node: The node to parse
        :type node: :class:`ast.Num`

        :returns: The value
        :rtype: numeric
        """
        return node.n

    #pylint: disable=invalid-name
    def visit_UnaryOp(self, node):
        """Parse :class:`ast.UnaryOp` nodes

        Inspects the unary operator and applies this to the result of the operand

        :param node: The node to parse
        :type node: :class:`ast.UnaryOp`

        :returns: The result
        :rtype: object
        """
        if isinstance(node.op, ast.USub):
            return -1 * self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return self.visit(node.operand)
        return None

    #pylint: disable=invalid-name
    def visit_BinOp(self, node):
        """Parse :class:`ast.BinOp` nodes

        Converts the binary operation into an evaluator

        :param node: The node to parse
        :type node: :class:`ast.BinOp`

        :returns: An evaluator that performs the operation described
        :rtype: :class:`ValueProxy`
        """
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        op_type = type(node.op)
        if not op_type in OP_NAMES or OP_NAMES[op_type] not in self._evaluator_library:
            raise SyntaxError('Invalid operator in {} at position {}'.format(self._value_proxy_string, node.col_offset))
        self._value_proxy = self._evaluator_library[OP_NAMES[op_type]](left_value, right_value)
        return self._value_proxy

    #pylint: disable=invalid-name
    def visit_Name(self, node):
        """Parse :class:`ast.Name` nodes

        If a macro, generator or parameter token is found, converts to an evaluator

        :param node: The node to parse
        :type node: :class:`ast.Name`

        :returns: An evaluator that performs the operation described if found, otherwise a string
        :rtype: :class:`ValueProxy`, str
        """
        if node.id.startswith(MACRO_TOKEN):
            macro_name = node.id.replace(MACRO_TOKEN, '')
            if not macro_name in self._macro_library:
                raise LookupError('Macro {} not found'.format(macro_name))
            self._value_proxy = self._macro_library[macro_name]
            return self._value_proxy
        if node.id.startswith(GENERATOR_TOKEN):
            generator_name = node.id.replace(GENERATOR_TOKEN, '')
            if not generator_name in self._generator_library:
                raise LookupError('Generator {} not found'.format(generator_name))
            self._value_proxy = self._generator_library[generator_name]
            return self._value_proxy
        if node.id.startswith(PARAMETER_TOKEN):
            parameter_name = node.id.replace(PARAMETER_TOKEN, '')
            self._value_proxy = ParameterEvaluator(parameter_name)
            return self._value_proxy
        return node.id

    @property
    def value_proxy(self):
        """The value_proxy

        If a value_proxy was found, it is accessible here. Otherwise returns None

        :returns: A value_proxy
        :rtype: :class:`ValueProxy`
        """
        return self._value_proxy

class ValueProxyParser:
    """Parser for value proxies
    """
    def __init__(self, value_libraries):
        """Initialises :class:`ValueProxyParser`

        :param value_libraries: A mapping between value library names (e.g. generators, evaluators, macros)
                                and value libraries.
                                The default is {}.
        :type value_libraries: dict
        """
        self._evaluator_library = value_libraries.evaluators
        self._generator_library = value_libraries.generators
        self._macro_library = value_libraries.macros

    def parse(self, value):
        """Parse the value string

        :param value: The value to convert to a value proxy
        :type value: str

        :returns: The value proxy, if any
        :rtype: :class:`ValueProxy`
        """
        if not self.is_value_proxy(value):
            raise ValueError('{} is not a value proxy'.format(value))
        tokenised_string = self._tokenise(value)
        tree = ast.parse(tokenised_string)
        visitor = ValueProxyVisitor(
            self._evaluator_library, self._macro_library, self._generator_library, tokenised_string
        )
        visitor.visit(tree)
        return visitor.value_proxy

    def is_value_proxy(self, value):
        """Determine if the provided string is a value proxy

        :param value: The value to analyse
        :type value: str

        :returns: ``True`` if the string provided is a value proxy; ``False`` otherwise
        :rtype: bool
        """
        if not isinstance(value, str):
            return False
        expanded_string = self._expand(value)
        return any(expanded_string.startswith(prefix + ':') for prefix in [GENERATOR, MACRO, EVALUATOR, PARAMETER])

    @staticmethod
    def _tokenise(input_string):
        output = ValueProxyParser._expand(input_string)
        for token, replacement in TOKENS.items():
            output = output.replace(token + ':', replacement)
        return output

    @staticmethod
    def _expand(input_string):
        output = input_string
        for token, replacement in SHORT_FORM_EXPANSION.items():
            output = output.replace(token, replacement + ':')
        return output
