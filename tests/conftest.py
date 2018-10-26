from os import path

import pytest

import luigi.configuration

example_data_folder = path.realpath('example_data')

EXE_PATHS = {
    'turbsim': path.join(example_data_folder, 'TurbSim.exe'),
    'fast': path.join(example_data_folder, 'FASTv7.0.2.exe')
}

@pytest.fixture(scope='session', autouse=True)
def configure_luigi():
    luigi.configuration.get_config().set('WindGenerationTask', '_runner_type', 'process')
    luigi.configuration.get_config().set('WindGenerationTask', '_exe_path', EXE_PATHS['turbsim'])
    luigi.configuration.get_config().set('FastSimulationTask', '_runner_type', 'process')
    luigi.configuration.get_config().set('FastSimulationTask', '_exe_path', EXE_PATHS['fast'])