from os import path, pardir
import luigi
from multiwindcalc.simulation_inputs import TurbsimInput, FastInput
from multiwindcalc.run_generator.fast_simulation_spawner import TurbsimSpawner, FastSimulationSpawner
from multiwindcalc.run_generator.generate_tasks import generate_tasks_from_spec
from multiwindcalc.parsers.specification import SpecificationNodeParser


__home_dir = path.dirname(path.realpath(__file__))
example_data_folder = path.join(__home_dir, pardir, 'example_data')


def create_spawner(output_base_dir):
    wind_spawner = TurbsimSpawner(path.join(output_base_dir, 'wind'),
                                  TurbsimInput.from_file(path.join(example_data_folder, 'fast_input_files',
                                                                   'TurbSim.inp')),
                                  path.join(example_data_folder, 'TurbSim.exe'))
    return FastSimulationSpawner(path.join(output_base_dir, 'runs'),
                                 FastInput.from_file(path.join(example_data_folder, 'fast_input_files',
                                                               'NRELOffshrBsline5MW_Onshore.fst')),
                                 path.join(example_data_folder, 'FASTv7.0.2.exe'),
                                 wind_spawner)


def test_can_run_one_turbsim_and_fast_run(tmpdir):
    spec = {
        "base_wind_input": path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp'),
        "wind_executable": path.join(example_data_folder, 'TurbSim.exe'),
        "base_time_domain_input": path.join(example_data_folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst'),
        "time_domain_executable": path.join(example_data_folder, 'FASTv7.0.2.exe'),
        "output_base_dir": tmpdir.strpath,
        "runs": [{'wind_speed': 8.0, 'output_start_time': 0.0, 'simulation_time': 1.0}]
    }
    spawner = create_spawner(tmpdir.strpath)
    run_spec = {'wind_speed': 8.0, 'output_start_time': 0.0, 'simulation_time': 1.0}
    root_node = SpecificationNodeParser().parse(run_spec)
    tasks = generate_tasks_from_spec(spawner, root_node)
    luigi.build(tasks, local_scheduler=True, log_level='WARNING')
    assert tasks[0].output().exists()
