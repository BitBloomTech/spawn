import json
from os import path

from luigi import configuration

from spawn.plugins.json_input_file import create_spawner
from spawn.tasks import SimulationTask


def test_when_creating_spawner_simulation_task_parameters_are_set_correctly(example_data_folder, tmpdir):
    fake_exe_path = __file__
    create_spawner(fake_exe_path, str(tmpdir), path.join(example_data_folder, 'example_spec.json'), 'process')
    luigi_config = configuration.get_config()
    assert fake_exe_path == luigi_config.get(SimulationTask.__name__, '_exe_path')
    assert tmpdir == luigi_config.get(SimulationTask.__name__, '_working_dir')
    assert 'process' == luigi_config.get(SimulationTask.__name__, '_runner_type')


def test_spawner_uses_correct_base_file(tmpdir):
    fake_exe_path = __file__
    base_file = path.join(tmpdir, 'base.json')
    with open(base_file, 'w') as fw:
        json.dump({'alpha': 'egg'}, fw)
    spawner = create_spawner(fake_exe_path, str(tmpdir), base_file, 'process')
    assert 'egg' == spawner.alpha
