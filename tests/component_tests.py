from os import path, pardir
import luigi
from multiwindcalc.run_generator.generate_tasks import generate_aeroelastic_simulations


__home_dir = path.dirname(path.realpath(__file__))
example_data_folder = path.join(__home_dir, pardir, 'example_data')


def test_can_run_one_turbsim_and_fast_run(tmpdir):
    spec = {
        "base_wind_input": path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp'),
        "wind_executable": path.join(example_data_folder, 'TurbSim.exe'),
        "base_time_domain_input": path.join(example_data_folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst'),
        "time_domain_executable": path.join(example_data_folder, 'FASTv7.0.2.exe'),
        "output_base_dir": tmpdir.strpath,
        "runs": [{'wind_speed': 8.0, 'output_start_time': 0.0, 'simulation_time': 1.0}]
    }
    tasks = generate_aeroelastic_simulations(spec)
    luigi.build(tasks, local_scheduler=True, log_level='WARNING')
    assert tasks[0].output().exists()
