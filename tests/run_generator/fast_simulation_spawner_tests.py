from os import path
import tempfile
import pytest
from multiwindcalc.run_generator.tasks import WindGenerationTask
from multiwindcalc.run_generator.fast_simulation_spawner import TurbsimSpawner, FastSimulationSpawner
from multiwindcalc.simulation_inputs.nrel_simulation_input import FastInput, TurbsimInput
from ..component_tests import example_data_folder

__examples_folder = path.join(example_data_folder, 'fast_input_files')
__turbsim_exe = path.join(example_data_folder, 'TurbSim.exe')
__fast_exe = path.join(example_data_folder, 'FASTv7.0.2.exe')


@pytest.fixture(scope='function')
def turbsim_input():
    return TurbsimInput.from_file(path.join(__examples_folder, 'TurbSim.inp'))


@pytest.fixture(scope='function')
def fast_input():
    return FastInput.from_file(path.join(__examples_folder, 'NRELOffshrBsline5MW_Onshore.fst'))


def test_can_spawn_turbsim_task(turbsim_input):
    temp_dir = tempfile.TemporaryDirectory()
    spawner = TurbsimSpawner(temp_dir.name, turbsim_input, __turbsim_exe)
    task = spawner.spawn()
    assert len(task.requires()) == 0
    assert task.wind_file_path == path.join(temp_dir.name, 'wind.wnd')
    assert not task.complete()


def test_spawns_fast_task_without_wind(turbsim_input, fast_input):
    temp_dir = tempfile.TemporaryDirectory()
    spawner = FastSimulationSpawner(temp_dir.name, fast_input, __fast_exe,
                                    TurbsimSpawner(temp_dir.name, turbsim_input, __turbsim_exe))
    task = spawner.spawn()
    assert len(task.requires()) == 0
    assert not task.complete()


def test_spawns_tests_requiring_wind_generation_when_wind_changed(turbsim_input, fast_input):
    temp_dir = tempfile.TemporaryDirectory()
    spawner = FastSimulationSpawner(temp_dir.name, fast_input, __fast_exe,
                                    TurbsimSpawner(temp_dir.name, turbsim_input, __turbsim_exe))
    task = spawner.spawn()
    assert len(task.requires()) == 0
    s2 = spawner.branch('a')
    s2.wind_speed = 8.0
    task2 = s2.spawn()
    assert isinstance(task2.requires()[0], WindGenerationTask)
    s2.simulation_time = 1.1
    task3 = s2.spawn()
    assert task3.requires()[0] is task2.requires()[0]
    s3 = spawner.branch('b')
    # wind file dependency is not yet carried through branching
    # task4 = s3.spawn()
    # assert task4.requires()[0] is task2.requires()[0]


