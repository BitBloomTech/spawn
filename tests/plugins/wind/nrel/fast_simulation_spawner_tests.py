from os import path, makedirs
import tempfile
import pytest
from multiwindcalc.plugins.wind.nrel import TurbsimSpawner, FastSimulationSpawner, FastInput, TurbsimInput, WindGenerationTask


@pytest.fixture(scope='function')
def turbsim_input(examples_folder):
    return TurbsimInput.from_file(path.join(examples_folder, 'TurbSim.inp'))


@pytest.fixture(scope='function')
def fast_input(examples_folder):
    return FastInput.from_file(path.join(examples_folder, 'NRELOffshrBsline5MW_Onshore.fst'))


def test_can_spawn_turbsim_task(turbsim_input):
    temp_dir = tempfile.TemporaryDirectory()
    spawner = TurbsimSpawner(turbsim_input)
    task = spawner.spawn(temp_dir.name, {})
    assert len(task.requires()) == 0
    assert task.wind_file_path == path.join(temp_dir.name, 'wind.wnd')
    assert not task.complete()


def test_spawns_fast_task_without_wind(turbsim_input, fast_input):
    temp_dir = tempfile.TemporaryDirectory()
    spawner = FastSimulationSpawner(fast_input, TurbsimSpawner(turbsim_input))
    task = spawner.spawn(temp_dir.name, {})
    assert len(task.requires()) == 0
    assert not task.complete()


def test_spawns_tests_requiring_wind_generation_when_wind_changed(turbsim_input, fast_input):
    temp_dir = tempfile.TemporaryDirectory()
    dir_a = path.join(temp_dir.name, 'a')
    dir_b = path.join(temp_dir.name, 'b')
    spawner = FastSimulationSpawner(fast_input, TurbsimSpawner(turbsim_input))
    task = spawner.spawn(dir_a, {})
    assert len(task.requires()) == 0
    s2 = spawner.branch()
    s2.wind_speed = 8.0
    task2 = s2.spawn(path.join(temp_dir.name, 'b'), {})
    assert isinstance(task2.requires()[0], WindGenerationTask)
    s2.simulation_time = 1.1
    task3 = s2.spawn(path.join(temp_dir.name, 'c'), {})
    assert task3.requires()[0] is task2.requires()[0]
    s3 = spawner.branch()
    # wind file dependency is not yet carried through branching
    # task4 = s3.spawn()
    # assert task4.requires()[0] is task2.requires()[0]


def test_spawn_with_additional_directory_puts_tasks_in_new_folders(turbsim_input, fast_input, tmpdir):
    runs_dir_1 = path.join(tmpdir, 'runs', '1')
    runs_dir_2 = path.join(tmpdir, 'runs', '2')
    spawner = FastSimulationSpawner(fast_input, TurbsimSpawner(turbsim_input))
    spawner.wind_speed = 6.0
    task1 = spawner.spawn(runs_dir_1, {})
    spawner.wind_speed = 8.0
    task2 = spawner.spawn(runs_dir_2, {})
    assert task1.output().path != task2.output().path
    assert task1.requires()[0].output().path != task2.requires()[0].output().path
