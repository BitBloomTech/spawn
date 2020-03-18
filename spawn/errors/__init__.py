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
"""Defines errors used in spawn
"""

class SpawnError(Exception):
    """Base class for all errors in spawn"""

class ParserError(SpawnError):
    """Base class for all parsing errors in spawn"""

class MacroNotFoundError(ParserError):
    """Error raised when a macro is not found
    """
    def __init__(self, macro_name):
        super().__init__('Macro "{}" not found'.format(macro_name))

class GeneratorNotFoundError(ParserError):
    """Error raised when a generator is not found
    """
    def __init__(self, generator_name):
        super().__init__('Generator "{}" not found'.format(generator_name))

class EvaluatorNotFoundError(ParserError):
    """Error raised when an evaluator is not found
    """
    def __init__(self, evaluator_name):
        super().__init__('Evaluator "{}" not found'.format(evaluator_name))

class ParameterNotFoundError(ParserError):
    """Error raised when a parameter argument to an evaluator is not found in the currently defined parameters
    """
    def __init__(self, parameter_name):
        self.parameter_name = parameter_name
        super().__init__('Parameter "{}" not found'.format(parameter_name))

class EvaluatorParameterNotFoundError(ParserError):
    """Error raised when a parameter argument to an evaluator is not found in the currently defined parameters
    """
    def __init__(self, parameter_name, evaluator_name):
        super().__init__('Parameter "{}" as argument to "{}" non-existent at this node'.format(parameter_name,
                                                                                               evaluator_name))

class EvaluatorTypeError(ParserError):
    """Error raised when an evaluator is provided with incorrect arguments
    """
    def __init__(self, evaluator_name, expected, actual):
        super().__init__(
            '{}() takes the following arguments: {} ({} provided)'.format(
                evaluator_name, ', '.join(expected), ', '.join(str(a) for a in actual)
            )
        )

class InvalidOperatorError(ParserError):
    """Error raised when an operator is invalid
    """
    def __init__(self, operator_name, position):
        super().__init__('Invalid operator in {} near position {}'.format(operator_name, position))

class SpecFormatError(ParserError):
    """Error raised when the format of the spec object is incorrect
    """
    def __init__(self, error):
        super().__init__('Invalid spec format: {}'.format(error))
