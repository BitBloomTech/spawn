# multiwindcalc
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
import pytest

from os import path

from multiwindcalc.util.validation import *

def test_validate_type_raises_for_invalid_type():
    with pytest.raises(TypeError):
        validate_type(123, str, 'value')

def test_validate_type_does_not_raise_for_valid_type():
    validate_type(42, int, 'value')

def test_validate_file_raises_for_non_existent_file(tmpdir):
    with pytest.raises(FileNotFoundError):
        validate_file(path.join(tmpdir, 'idonotexist'), 'file')

def test_validate_file_does_not_raise_for_existing_file(tmpdir):
    existing_file = path.join(tmpdir, 'iamhere')
    with open(existing_file, 'w'):
        pass
    validate_file(existing_file, 'file')

def test_validate_folder_raises_for_non_existent_folder():
    with pytest.raises(FileNotFoundError):
        validate_dir('CDE:/I/do/not/exist', 'folder')

def test_validate_folder_does_not_raise_for_existent_folder(tmpdir):
    validate_dir(tmpdir, 'folder')

