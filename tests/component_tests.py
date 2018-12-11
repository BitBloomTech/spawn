from os import path, pardir
import luigi
from multiwindcalc.generate_tasks import generate_tasks_from_spec
from multiwindcalc.parsers.specification_parser import SpecificationNodeParser
from multiwindcalc.parsers.value_proxy import ValueProxyParser


def test_can_run_one_turbsim_and_fast_run(tmpdir, example_data_folder, spawner):
    spec = {
        "base_wind_input": path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp'),
        "wind_executable": path.join(example_data_folder, 'TurbSim.exe'),
        "base_time_domain_input": path.join(example_data_folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst'),
        "time_domain_executable": path.join(example_data_folder, 'FASTv7.0.2.exe'),
        "output_base_dir": tmpdir.strpath,
        "runs": [{'wind_speed': 8.0, 'output_start_time': 0.0, 'simulation_time': 1.0}]
    }
    run_spec = {
        'wind_speed': 8.0, 'output_start_time': 0.0, 'simulation_time': 1.0
    }
    root_node = SpecificationNodeParser(ValueProxyParser({})).parse(run_spec)
    tasks = generate_tasks_from_spec(spawner, root_node, tmpdir.strpath)
    luigi.build(tasks, local_scheduler=True, log_level='WARNING')
    assert tasks[0].output().exists()
