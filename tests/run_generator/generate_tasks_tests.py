import os.path as path
import tempfile
from ..component_tests import example_data_folder
from multiwindcalc.run_generator.generate_tasks import generate_aeroelastic_simulations
from multiwindcalc.run_generator.tasks import SimulationTask, WindGenerationTask


def test_can_create_set_of_aeroelastic_tasks():
    temp_dir = tempfile.TemporaryDirectory()
    spec = {
        "base_wind_input": path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp'),
        "wind_executable": path.join(example_data_folder, 'TurbSim.exe'),
        "base_time_domain_input": path.join(example_data_folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst'),
        "time_domain_executable": path.join(example_data_folder, 'FASTv7.0.2.exe'),
        "output_base_dir": temp_dir.name,
        "runs": [
            {
                'wind_speed': 4.0
            },
            {
                'wind_speed': 6.0
            },
            {
                'wind_speed': 8.0
            },
            {
                'wind_speed': 10.0
            },
            {
                'wind_speed': 12.0
            },
            {
                'wind_speed': 14.0
            },
        ]
    }
    tasks = generate_aeroelastic_simulations(spec)
    assert len(tasks) == 6
    for t in tasks:
        assert isinstance(t, SimulationTask)
        assert len(t.requires()) == 1
        assert isinstance(t.requires()[0], WindGenerationTask)
