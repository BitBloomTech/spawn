from os import path
import tempfile
from ..tasks import SimulationTask, WindGenerationTask
from multiwindcalc.component_tests import example_data_folder


def _check_run_fails(task, error_file):
    try:
        task.run()
        assert False
    except ChildProcessError:
        assert path.isfile(error_file)


def test_runs_fast_with_error():
    temp_dir = tempfile.TemporaryDirectory()
    input_file = path.join(temp_dir.name, 'fast.ipt')
    with open(input_file, 'w') as fp:
        fp.write('some bad FAST input data')
    task = SimulationTask('foo', path.join(example_data_folder, 'FASTv7.0.2.exe'), input_file)
    _check_run_fails(task, path.join(temp_dir.name, 'fast.err'))


def test_run_wind_generation_task_with_error():
    temp_dir = tempfile.TemporaryDirectory()
    input_file = path.join(temp_dir.name, 'turbsim.ipt')
    task = WindGenerationTask('wind', path.join(example_data_folder, 'TurbSim.exe'), input_file)
    _check_run_fails(task, path.join(temp_dir.name, 'turbsim.err'))
