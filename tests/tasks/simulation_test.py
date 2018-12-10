import pytest

from multiwindcalc.tasks import SimulationTask

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