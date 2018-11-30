"""Contains utility functions for hashing entitiess
"""
import hashlib

from multiwindcalc.util.validation import validate_file

def file_hash(filename):
    validate_file(filename, 'filename')
    h = hashlib.new('md5')
    with open(filename, 'rb') as fp:
        h.update(fp.read())
    return h.digest()
