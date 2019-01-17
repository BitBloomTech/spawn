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
"""Methods to assist with parameter validation
"""
from os import path

def validate_type(value, expected, name):
    """Validates that the value is of the expected type.

    Raises ``TypeError`` if not.

    Parameters
    ----------
    value : obj
        Value to validate
    expected : type
        The expected type
    name : str
        The name of the value
    """
    if not isinstance(value, expected):
        raise TypeError(
            '{} must be of type {}; was {}'.format(
                name, expected.__name__, type(value).__name__
            )
        )


def validate_file(value, name):
    """Validates that the given file exists and is accessible.

    Raises ``FileNotFoundError`` if not.

    Parameters
    ----------
    value : str or path-like
        Path to the file to validate
    name : str
        The name of the value
    """
    if value is None:
        raise ValueError('File not defined for {}'.format(name))
    if not path.isfile(value):
        raise FileNotFoundError('File {} not found or not accessible at {}'.format(name, value))


def validate_dir(value, name):
    """Validates that the given folder exists and is accessible.

    Raises ``FileNotFoundError`` if not.

    Parameters
    ----------
    value : str or path-like
        Path to the folder to validate
    name : str
        The name of the value
    """
    if value is None:
        raise ValueError('Folder not defined for {}'.format(name))
    if not path.isdir(value):
        raise FileNotFoundError('Folder {} not found or not accessible at {}'.format(name, value))
