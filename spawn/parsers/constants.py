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
EVALUATOR_SHORT = '#'

RANGE = 'range'
REPEAT = 'repeat'
MULTIPLY = 'mult'
DIVIDE = 'divide'
ADD = 'add'
SUBTRACT = 'sub'

SHORT_FORM_EXPANSION = {
    GENERATOR_SHORT: GENERATOR,
    MACRO_SHORT: MACRO,
    PARAMETER_SHORT: PARAMETER,
    EVALUATOR_SHORT: EVALUATOR
}
