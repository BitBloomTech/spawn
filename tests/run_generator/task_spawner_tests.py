from os import path
import tempfile
import luigi
from multiwindcalc.run_generator.task_spawner import FastTaskSpawner
from multiwindcalc.simulation_inputs.nrel_simulation_input import FastInput, TurbsimInput
from ..component_tests import example_data_folder


def test_can_run_single_run_including_wind():
    temp_dir = tempfile.TemporaryDirectory()
    spawner = FastTaskSpawner(temp_dir.name,
                              FastInput(path.join(example_data_folder, 'fast_input_files',
                                                        'NRELOffshrBsline5MW_Onshore.fst')),
                              TurbsimInput(path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp')),
                              path.join(example_data_folder, 'FASTv7.0.2.exe'),
                              path.join(example_data_folder, 'TurbSim.exe'))
    task = spawner.spawn({'wind_speed': 7.3})
    luigi.build([task], local_scheduler=True)
    path.isfile(task.output().path)
