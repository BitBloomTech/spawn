# spawn
# Copyright (C) 2018, Simmovation Ltd.
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
    validate_file(filename, 'filename')
    with open(filename, 'rb') as fp:
        return bytes_hash(fp.read())

def bytes_hash(value):
    validate_type(value, bytes, 'value')
    h = hashlib.new('md5')
    h.update(value)
    return h.hexdigest()

def string_hash(string):
    validate_type(string, str, 'string')
    return bytes_hash(string.encode('utf8'))
