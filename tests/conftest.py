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
from os import path, pardir

import pytest

import luigi.configuration

from spawn.config import DefaultConfiguration
from spawn.plugins import PluginLoader
from spawn.tasks import SpawnTask, TaskListParameter
from spawn.spawners import TaskSpawner

__home_dir = path.dirname(path.realpath(__file__))
_example_data_folder = path.join(__home_dir, pardir, 'example_data')

class _TestTask(SpawnTask):
    run_registry = []

    @property
    def _args(self):
        return {'task': type(self).__name__, 'metadata': self._metadata}

    def run(self):
        self.run_registry.append(self._args)
    
    def complete(self):
        return self._args in self.run_registry

class FooTask(_TestTask):
    pass

class BarTask(_TestTask):
    pass


class FooSpawner(TaskSpawner):
    def __init__(self, run_registry):
        self._run_registry = run_registry

    def spawn(self, path, metadata):
        task = FooTask(_id=path, _metadata=metadata, )
        task.run_registry = self._run_registry
        return task
    
    def branch(self):
        return FooSpawner(self._run_registry)

class BarSpawner(TaskSpawner):
    def __init__(self, foo_spawner, run_registry):
        self._foo_spawner = foo_spawner
        self._run_registry = run_registry

    def spawn(self, path, metadata):
        task = BarTask(_id=path, _dependencies=[self._foo_spawner.spawn(path, metadata)], _metadata=metadata)
        task.run_registry = self._run_registry
        return task

    def branch(self):
        return BarSpawner(self._foo_spawner.branch(), self._run_registry)

@pytest.fixture
def run_registry():
    return []

@pytest.fixture
def spawner(run_registry):
    return BarSpawner(FooSpawner(run_registry), run_registry)

@pytest.fixture
def example_data_folder():
    return _example_data_folder

@pytest.fixture
def plugin_loader():
    return PluginLoader(DefaultConfiguration())
