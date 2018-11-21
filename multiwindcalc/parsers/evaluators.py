"""Implements the evaluators parser
"""

import ast

from multiwindcalc.specification.evaluators import ParameterEvaluator

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

TOKENS = {
    MACRO: MACRO_TOKEN,
    GENERATOR: GENERATOR_TOKEN,
    PARAMETER: PARAMETER_TOKEN
}

class EvaluatorVisitor(ast.NodeVisitor):
    """Implementation of :class:`ast.NodeVisitor` that is able to parse evaluators
    """
    def __init__(self, evaluator_library, macro_library, generator_library, evaluator_string):
        """Initialises :class:`EvaluatorVisitor`

        :param evaluator_library: The evaluator library
        :type evaluator_library: dict
        :param macro_library: The macro library
        :type macro_library: dict
        :param generator_library: The generator library
        :type generator_library: dict
        :param evaluator_string: The string to be evaluated
        :type evaluator_string: str 
        """
        self._evaluator_library = evaluator_library
        self._macro_library = macro_library
        self._generator_library = generator_library
        self._evaluator_string = evaluator_string
        self._evaluator = None

    def visit_Call(self, node):
        """Parse :class:`ast.Call` nodes

        Recursively calls :method:`visit` on args
        
        :param node: The node to parse
        :type node: :class:`ast.Call`

        :returns: An evaluator parsed from the node
        :rtype: :class:`ValueProxy`
        """
        arg_values = [self.visit(a) for a in node.args]
        if any(a is None for a in arg_values):
            null_arg_index = arg_values.index(None)
            offset = node.args[null_arg_index].col_offset
            raise SyntaxError('Invalid syntax in {} at position {}'.format(self._evaluator_string, offset))
        if node.func.id not in self._evaluator_library:
            raise LookupError('Evaluator {} not found'.format(node.func.id))
        self._evaluator = self._evaluator_library[node.func.id](*arg_values)
        return self._evaluator
    
    def visit_Num(self, node):
        """Parse :class:`ast.Num` nodes

        Returns the value at the node
        
        :param node: The node to parse
        :type node: :class:`ast.Num`

        :returns: The value
        :rtype: numeric
        """
        return node.n

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
            raise SyntaxError('Invalid operator in {} at position {}'.format(self._evaluator_string, node.col_offset))
        self._evaluator = self._evaluator_library[OP_NAMES[op_type]](left_value, right_value)
        return self._evaluator
    
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
            self._evaluator = self._macro_library[macro_name]
            return self._evaluator
        if node.id.startswith(GENERATOR_TOKEN):
            generator_name = node.id.replace(GENERATOR_TOKEN, '')
            if not generator_name in self._generator_library:
                raise LookupError('Generator {} not found'.format(generator_name))
            self._evaluator = self._generator_library[generator_name]
            return self._evaluator
        if node.id.startswith(PARAMETER_TOKEN):
            parameter_name = node.id.replace(PARAMETER_TOKEN, '')
            self._evaluator = ParameterEvaluator(parameter_name)
            return self._evaluator
        return node.id

    @property
    def evaluator(self):
        """The evaluator

        If an evaluator was found, it is accessible here. Otherwise returns None

        :returns: An evaluator
        :rtype: :class:`ValueProxy`
        """
        return self._evaluator

class EvaluatorParser:
    """Parser for evaluators
    """
    def __init__(self, value_libraries):
        """Initialises :class:`EvaluatorParser`

        :param value_libraries: A mapping between value library names (e.g. generators, evaluators, macros)
                                and value libraries.
                                The default is {}.
        :type value_libraries: dict
        """
        self._evaluator_library = value_libraries.get(EVALUATOR, {})
        self._macro_library = value_libraries.get(MACRO, {})
        self._generator_library = value_libraries.get(GENERATOR, {})

    def parse(self, evaluator_string):
        """Parse the evaluator string

        :param evaluator_string: The evaluator string to convert to an evaluator
        :type evaluator_string: str

        :returns: The evaluator for the evaluator string, if any
        :rtype: :class:`ValueProxy`
        """
        tokenised_string = self._tokenise(evaluator_string)
        tree = ast.parse(tokenised_string)
        visitor = EvaluatorVisitor(self._evaluator_library, self._macro_library, self._generator_library, tokenised_string)
        visitor.visit(tree)
        return visitor.evaluator
    
    def is_evaluator(self, evaluator_string):
        """Determine if the provided string is an evaluator

        :param evaluator_string: The evaluator string to analyse
        :type evaluator_string: str

        :returns: ``True`` if the string provided is an evaluator; ``False`` otherwise
        :rtype: bool
        """
        try:
            return self.parse(evaluator_string) is not None
        except SyntaxError:
            return False
    
    @staticmethod
    def _tokenise(input_string):
        output = input_string
        for token, replacement in SHORT_FORM_EXPANSION.items():
            output = output.replace(token, replacement + ':')
        for token, replacement in TOKENS.items():
            output = output.replace(token + ':', replacement)
        return output
