"""Contains utility functions for hashing entitiess
"""
import hashlib

from multiwindcalc.util.validation import validate_file, validate_type

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
