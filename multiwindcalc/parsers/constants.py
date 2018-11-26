"""Defines constants for the parsers module
"""

COMBINATOR = 'combine'
GENERATOR = 'gen'
PARAMETER = 'param'
MACRO = 'macro'
EVALUATOR = 'eval'
ZIP = 'zip'
PRODUCT = 'product'
POLICY = 'policy'
PATH = 'path'
GHOST = '_'

GENERATOR_SHORT = '@'
MACRO_SHORT = '$'
PARAMETER_SHORT = '!'

RANGE = 'range'
REPEAT = 'repeat'
MULTIPLY = 'mult'
DIVIDE = 'divide'
ADD = 'add'
SUBTRACT = 'sub'

SHORT_FORM_EXPANSION = {
    GENERATOR_SHORT: GENERATOR,
    MACRO_SHORT: MACRO,
    PARAMETER_SHORT: PARAMETER
}
