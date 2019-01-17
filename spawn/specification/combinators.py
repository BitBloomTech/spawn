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
"""This module defines combinators for use in the ``SpecificationParser``

An combinator is a function or object that can be called.

It takes a single argument, which should be of type `dict` and is a
mapping between property names and property values.

It returns a `list` of `dict` mappings between property names and
property values
"""

def zip_properties(value):
    """Combines properties by zipping the values provided

    Parameters
    ----------
    value : dict
        Mapping of properties to lists of values

    Returns
    -------
    result : list of dict
        List of combined properties
    """
    if not isinstance(value, dict):
        raise TypeError('value {} must be of type dict, but was {}'.format(value, type(value)))
    if not value:
        raise ValueError('value is empty')
    if not all(isinstance(v, list) for v in value.values()):
        raise ValueError('value {} must have all list values'.format(value))
    values_list = list(value.values())
    if not all(len(l) == len(values_list[0]) for l in values_list):
        raise ValueError('all lists in value {} were not the same length'.format(value))
    return [{k: v for k, v in zip(value.keys(), values)} for values in zip(*values_list)]

def product(value):
    """Combines properties by generating the Cartesian product of items in the first value with the remaining values

    Parameters
    ----------
    value : dict
        Mapping of properties to lists of values

    Returns
    -------
    result : list of dict
        List of combined properties
    """
    if not isinstance(value, dict):
        raise TypeError('value {} must be of type dict, but was {}'.format(value, type(value)))
    if not value:
        return []
    next_key, next_values = list(value.items())[0]
    if not isinstance(next_values, list):
        return [value]
    return [{next_key: next_value, **{k: v for k, v in value.items() if k != next_key}} for next_value in next_values]
