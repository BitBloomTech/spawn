import os.path as path
import numpy as np
from ..component_tests import example_data_folder
from multiwindcalc.run_generator.generate_tasks import generate_aeroelastic_simulations
from multiwindcalc.run_generator.tasks import SimulationTask, WindGenerationTask


def test_can_create_set_of_aeroelastic_tasks(tmpdir):
    spec = {
        "base_wind_input": path.join(example_data_folder, 'fast_input_files', 'TurbSim.inp'),
        "wind_executable": path.join(example_data_folder, 'TurbSim.exe'),
        "base_time_domain_input": path.join(example_data_folder, 'fast_input_files', 'NRELOffshrBsline5MW_Onshore.fst'),
        "time_domain_executable": path.join(example_data_folder, 'FASTv7.0.2.exe'),
        "output_base_dir": tmpdir.strpath,
        "runs": [{'wind_speed': v} for v in np.arange(4.0, 15.0, 2.0)]
    }
    tasks = generate_aeroelastic_simulations(spec)
    assert len(tasks) == 6
    for t in tasks:
        assert isinstance(t, SimulationTask)
        assert len(t.requires()) == 1
        assert isinstance(t.requires()[0], WindGenerationTask)
        assert path.isdir(path.split(t.run_name_with_path)[0])
        assert spec['output_base_dir'] in t.run_name_with_path
        assert 'wind_speed' in t.metadata
