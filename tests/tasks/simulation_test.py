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
import pytest

from spawn.tasks import SimulationTask

@pytest.fixture
def task():
    return SimulationTask(_id='foo', _input_file_path='input_path', _runner_type='type', _metadata={'bar': 42, 'baz': 'hello'}, _exe_path='exe_path')

@pytest.fixture
def task_with_dependency(task):
    return SimulationTask(_id='foo_with_dependency', _input_file_path='input_path', _runner_type='type', _metadata={'bar': 42, 'baz': 'hello'}, _exe_path='exe_path', _dependencies=[task])

def test_can_serialize_simulation_task(task):
    assert task.to_str_params() is not None

def test_can_deserialize_simulation_task(task):
    s = task.to_str_params()
    deserialized = SimulationTask.from_str_params(s)
    assert deserialized == task

def test_can_serialize_simulation_task_with_dependencies(task, task_with_dependency):
    assert task_with_dependency.to_str_params() is not None
    
def test_can_deserialize_simulation_task_with_dependencies(task, task_with_dependency):
    s = task_with_dependency.to_str_params()
    deserialized = SimulationTask.from_str_params(s)
    assert deserialized == task_with_dependency
    assert deserialized._dependencies == (task,)