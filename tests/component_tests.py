import json
import tempfile
from os import path, pardir
from multiwindcalc.run_generator.run_generator import generate_preprocessing_runs, generate_time_domain_runs
from multiwindcalc.run_generator.batch import Batch


__home_dir = path.dirname(path.realpath(__file__))
example_data_folder = path.join(__home_dir, pardir, 'example_data')


def test_can_run_one_turbsim_and_fast_run():
    with open('./example_data/dlc_spec.json', 'r') as fp:
        spec = json.load(fp)

    with tempfile.TemporaryDirectory() as temp_dir:
        batch = Batch(temp_dir)
        generate_preprocessing_runs(spec, temp_dir, batch)
        batch.execute()
        generate_time_domain_runs(spec, temp_dir, batch)
        batch.execute()
        assert path.isdir(path.join(temp_dir, 'wind'))
        assert path.isdir(path.join(temp_dir, 'runs'))
        run1_dir = path.join(temp_dir, 'runs', 'a', '1')
        assert path.isfile(path.join(run1_dir, 'NRELOffshrBsline5MW_Onshore.outb'))
