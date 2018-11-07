from os import path, pardir

import pytest

import luigi.configuration

from multiwindcalc.plugins.wind.nrel import TurbsimInput, FastInput, TurbsimSpawner, FastSimulationSpawner

__home_dir = path.dirname(path.realpath(__file__))
_example_data_folder = path.join(__home_dir, pardir, 'example_data')

EXE_PATHS = {
    'turbsim': path.join(_example_data_folder, 'TurbSim.exe'),
    'fast': path.join(_example_data_folder, 'FASTv7.0.2.exe')
}

@pytest.fixture
def example_data_folder():
    return _example_data_folder

@pytest.fixture
def examples_folder(example_data_folder):
    return path.join(example_data_folder, 'fast_input_files')

@pytest.fixture
def turbsim_exe(example_data_folder):
    return path.join(example_data_folder, 'TurbSim.exe')

@pytest.fixture
def fast_exe(example_data_folder):
    return path.join(example_data_folder, 'FASTv7.0.2.exe')

@pytest.fixture(scope='session', autouse=True)
def configure_luigi():
    luigi.configuration.get_config().set('WindGenerationTask', '_runner_type', 'process')
    luigi.configuration.get_config().set('WindGenerationTask', '_exe_path', EXE_PATHS['turbsim'])
    luigi.configuration.get_config().set('FastSimulationTask', '_runner_type', 'process')
    luigi.configuration.get_config().set('FastSimulationTask', '_exe_path', EXE_PATHS['fast'])

@pytest.fixture
def spawner(example_data_folder):
    wind_spawner = TurbsimSpawner(TurbsimInput.from_file(path.join(example_data_folder, 'fast_input_files',
                                                                   'TurbSim.inp')))
    return FastSimulationSpawner(FastInput.from_file(path.join(example_data_folder, 'fast_input_files',
                                                               'NRELOffshrBsline5MW_Onshore.fst')),
                                 wind_spawner)