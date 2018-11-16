"""Implements the evaluators parser
"""

import ast

from multiwindcalc.specification.evaluators import ParameterEvaluator

from .specification_parser import SHORT_FORM_EXPANSION, MACRO, GENERATOR

OP_NAMES = {
    ast.Mult: 'mult',
    ast.Div: 'div',
    ast.Add: 'add',
    ast.Sub: 'sub'
}

MACRO_TOKEN = '__macro__'
GENERATOR_TOKEN = '__generator__'

TOKENS = {
    MACRO: MACRO_TOKEN,
    GENERATOR: GENERATOR_TOKEN
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
        arg_values = [self.visit(a) for a in node.args]
        if any(a is None for a in arg_values):
            null_arg_index = arg_values.index(None)
            offset = node.args[null_arg_index].col_offset
            raise SyntaxError('Invalid syntax in {} at position {}'.format(self._evaluator_string, offset))
        if node.func.id not in self._evaluator_library:
            raise SyntaxError('Evaluator {} not found'.format(node.func.id))
        self._evaluator = self._evaluator_library[node.func.id](*arg_values)
        return self._evaluator
    
    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        op_type = type(node.op)
        if not op_type in OP_NAMES or OP_NAMES[op_type] not in self._evaluator_library:
            raise SyntaxError('Invalid operator in {} at position {}'.format(self._evaluator_string, node.col_offset))
        self._evaluator = self._evaluator_library[OP_NAMES[op_type]](left_value, right_value)
        return self._evaluator
    
    def visit_Name(self, node):
        if node.id.startswith(MACRO_TOKEN):
            macro_name = node.id.replace(MACRO_TOKEN, '')
            if not macro_name in self._macro_library:
                raise SyntaxError('Macro {} not found'.format(macro_name))
            self._evaluator = self._macro_library[macro_name]
            return self._evaluator
        if node.id.startswith(GENERATOR_TOKEN):
            generator_name = node.id.replace(GENERATOR_TOKEN, '')
            if not generator_name in self._generator_library:
                raise SyntaxError('Generator {} not found'.format(generator_name))
            self._evaluator = self._generator_library[generator_name]
            return self._evaluator
        self._evaluator = ParameterEvaluator(node.id)
        return self._evaluator

    @property
    def evaluator(self):
        return self._evaluator

class EvaluatorParser:
    """Parser for evaluators
    """
    def __init__(self, evaluator_library, macro_library, generator_library):
        """Initialises :class:`EvaluatorParser`

        :param evaluator_library: The evaluator library
        :type evaluator_library: dict
        :param macro_library: The macro library
        :type macro_library: dict
        :param generator_library: The generator library
        :type generator_library: dict
        """
        self._evaluator_library = evaluator_library
        self._macro_library = macro_library
        self._generator_library = generator_library

    def parse(self, evaluator_string):
        """Parse the evaluator string

        :returns: The evaluator for the evaluator string, if any
        :rtype: :class:`ValueProxy`
        """
        tokenised_string = self._tokenise(evaluator_string)
        tree = ast.parse(tokenised_string)
        visitor = EvaluatorVisitor(self._evaluator_library, self._macro_library, self._generator_library, tokenised_string)
        visitor.visit(tree)
        return visitor.evaluator
    
    @staticmethod
    def _tokenise(input_string):
        output = input_string
        for token, replacement in SHORT_FORM_EXPANSION.items():
            output = output.replace(token, replacement + ':')
        for token, replacement in TOKENS.items():
            output = output.replace(token + ':', replacement)
        return output
