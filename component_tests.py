import json
import tempfile
import os
import os.path as path
from run_generator.run_generator import generate_preprocessing_runs, generate_time_domain_runs
from run_generator.batch import Batch


__home_dir = path.dirname(path.realpath(__file__))
example_data_folder = path.join(__home_dir, 'example_data')


def test_can_run_one_turbsim_and_fast_run():
    os.chdir(path.join(__home_dir, 'example_data'))
    with open('dlc_spec.json', 'r') as fp:
        spec = json.load(fp)

    temp_dir = tempfile.TemporaryDirectory()
    batch = Batch(temp_dir.name)
    generate_preprocessing_runs(spec, temp_dir.name, batch)
    batch.execute()
    generate_time_domain_runs(spec, temp_dir.name, batch)
    batch.execute()
    assert(path.isdir(path.join(temp_dir.name, 'wind')))
    assert(path.isdir(path.join(temp_dir.name, 'runs')))
    run1_dir = path.join(temp_dir.name, 'runs', 'a', '1')
    assert(path.isfile(path.join(run1_dir, 'NRELOffshrBsline5MW_Onshore.outb')))
