import pytest

from os import path

from multiwindcalc.util.validation import *

def test_validate_type_raises_for_invalid_type():
    with pytest.raises(TypeError):
        validate_type(123, str, 'value')

def test_validate_type_does_not_raise_for_valid_type():
    validate_type(42, int, 'value')

def test_validate_file_raises_for_non_existant_file(tmpdir):
    with pytest.raises(FileNotFoundError):
        validate_file(path.join(tmpdir, 'idonotexist'), 'file')

def test_validate_file_does_not_raise_for_existing_file(tmpdir):
    existing_file = path.join(tmpdir, 'iamhere')
    with open(existing_file, 'w'):
        pass
    validate_file(existing_file, 'file')