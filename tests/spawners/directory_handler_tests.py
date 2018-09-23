import tempfile
import os.path as path
from multiwindcalc.spawners.directory_handler import DirectoryHandler


def test_abspath_exists():
    temp_dir = tempfile.TemporaryDirectory()
    dh = DirectoryHandler(temp_dir.name)
    assert path.isdir(dh.abspath)


def test_abspath_exists_with_relative_path():
    temp_dir = tempfile.TemporaryDirectory()
    dh = DirectoryHandler(temp_dir.name, path.join('a', 'b'))
    assert path.isdir(dh.abspath)


def test_branch_makes_new_dir():
    temp_dir = tempfile.TemporaryDirectory()
    dh = DirectoryHandler(temp_dir.name)
    branch = dh.branch('runs')
    assert branch.abspath == path.join(dh.abspath, 'runs')
    branch2 = branch.branch('a')
    assert branch2.abspath == path.join(dh.abspath, 'runs', 'a')


def test_branching_with_default_dirs():
    temp_dir = tempfile.TemporaryDirectory()
    dh = DirectoryHandler(temp_dir.name)
    dh.branch()
    dh.branch()
    b3 = dh.branch()
    assert b3.abspath == path.join(dh.abspath, '3')
