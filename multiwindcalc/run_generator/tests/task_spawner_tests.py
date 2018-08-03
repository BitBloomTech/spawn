from os import path
import tempfile
import luigi
from ..task_spawner import FastTaskSpawner
from multiwindcalc.component_tests import example_data_folder
from multiwindcalc.input_editors.nrel_input_editor import FastInputEditor, TurbSimInputEditor


def test_can_run_single_run_including_wind():
    temp_dir = tempfile.TemporaryDirectory()
    spawner = FastTaskSpawner(temp_dir.name,
                              FastInputEditor(path.join(example_data_folder, 'fast_input_files',
                                                        'NRELOffshrBsline5MW_Onshore.fst')),
                              TurbSimInputEditor(path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp')),
                              path.join(example_data_folder, 'FASTv7.0.2.exe'),
                              path.join(example_data_folder, 'TurbSim.exe'))
    task = spawner.spawn({'wind_speed': 7.3})
    luigi.build([task], local_scheduler=True)
    path.isfile(task.output().path)
