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
from os import path

import pytest

from multiwindcalc.util.hash import *

def create_file(tmpdir, contents, name):
    filename = path.join(tmpdir, name)
    with open(filename, 'w') as fp:
        fp.write(contents)
    return filename

@pytest.fixture
def file_a(tmpdir):
    return create_file(tmpdir, 'This is file a', 'file_a.txt')

@pytest.fixture
def file_b(tmpdir):
    return create_file(tmpdir, 'This is file b', 'file_b.txt')

@pytest.fixture
def file_a_copy(tmpdir):
    return create_file(tmpdir, 'This is file a', 'file_a_copy.txt')

def test_file_returns_hash(file_a):
    assert file_hash(file_a)

def test_different_contents_return_different_hashes(file_a, file_b):
    assert file_hash(file_a) != file_hash(file_b)

def test_same_content_different_files_returns_same_hash(file_a, file_a_copy):
    assert file_hash(file_a) == file_hash(file_a_copy)

def test_same_file_returns_same_hash(file_a):
    assert file_hash(file_a) == file_hash(file_a)

def test_same_strings_same_hashes():
    assert string_hash('hello world') == string_hash('hello world')

def test_different_strings_different_hashes():
    assert string_hash('foo') != string_hash('bar')

def test_same_bytes_same_hashes():
    assert bytes_hash(b'hello world') == bytes_hash(b'hello world')

def test_different_bytes_different_hashes():
    assert bytes_hash(b'foo') != bytes_hash(b'bar')
