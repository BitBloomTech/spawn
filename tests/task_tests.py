from os import path
import tempfile
from multiwindcalc.tasks.simulation import FastSimulationTask, WindGenerationTask
from tests.component_tests import example_data_folder


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
    task = FastSimulationTask('foo', input_file)
    _check_run_fails(task, path.join(temp_dir.name, 'fast.err'))


def test_run_wind_generation_task_with_error():
    temp_dir = tempfile.TemporaryDirectory()
    input_file = path.join(temp_dir.name, 'turbsim.ipt')
    with open(input_file, 'w') as fp:
        fp.write('some bad wind input data')
    task = WindGenerationTask('wind', input_file)
    _check_run_fails(task, path.join(temp_dir.name, 'turbsim.err'))
