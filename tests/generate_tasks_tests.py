from os import path
import numpy as np
from tests.component_tests import example_data_folder, create_spawner
from multiwindcalc.generate_tasks import generate_tasks_from_spec
from multiwindcalc.tasks.simulation import SimulationTask, WindGenerationTask
from multiwindcalc.parsers import *


def test_can_create_1d_set_of_aeroelastic_tasks(tmpdir):
    spawner = create_spawner()
    run_spec = {'wind_speed': list(np.arange(4.0, 15.0, 2.0))}
    root_node = SpecificationNodeParser().parse(run_spec)
    tasks = generate_tasks_from_spec(spawner, root_node, tmpdir.strpath)
    assert len(tasks) == 6
    for t in tasks:
        assert isinstance(t, SimulationTask)
        assert len(t.requires()) == 1
        assert isinstance(t.requires()[0], WindGenerationTask)
        assert path.isdir(path.split(t.run_name_with_path)[0])
        assert tmpdir.strpath in t.run_name_with_path
        assert 'wind_speed' in t.metadata


def test_can_create_runs_from_tree_spec(tmpdir):
    spawner = create_spawner()
    input_path = path.join(example_data_folder, 'iec_fatigue_spec.json')
    spec_model = SpecificationParser(SpecificationFileReader(input_path)).parse()
    runs = generate_tasks_from_spec(spawner, spec_model.root_node, tmpdir.strpath)
    assert len(runs) == 12*3 + 12*2 + 12*3
    seeds = []
    for t in runs:
        assert isinstance(t, SimulationTask)
        assert len(t.requires()) == 1
        assert isinstance(t.requires()[0], WindGenerationTask)
        assert path.isdir(path.split(t.run_name_with_path)[0])
        assert tmpdir.strpath in t.run_name_with_path
        assert 'wind_speed' in t.metadata
        assert 'turbulence_seed' in t.metadata
        assert 'wind_direction' in t.metadata
        seeds.append(t.metadata['turbulence_seed'])
    assert len(seeds) != len(set(seeds))  # testing uniqueness
