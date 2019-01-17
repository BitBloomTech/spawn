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
"""Contains utility functions for hashing entitiess
"""
import hashlib

from spawn.util.validation import validate_file, validate_type

def file_hash(filename):
    """Returns the hash of a file

    :param filename: The filename to compute the hash of
    :type filename: path-like

    :returns: The MD5 hash of the file
    :rtype: bytes
    """
    validate_file(filename, 'filename')
    with open(filename, 'rb') as fp:
        return bytes_hash(fp.read())

def bytes_hash(value):
    """Returns the hash of a byte array

    :param value: The bytes to compute the hash of
    :type value: byte string

    :returns: The MD5 hash of the bytes
    :rtype: bytes
    """
    validate_type(value, bytes, 'value')
    hasher = hashlib.new('md5')
    hasher.update(value)
    return hasher.hexdigest()

def string_hash(string):
    """Returns the hash of a string

    :param filename: The string to compute the hash of
    :type filename: str

    :returns: The MD5 hash of the string
    :rtype: bytes
    """
    validate_type(string, str, 'string')
    return bytes_hash(string.encode('utf8'))
