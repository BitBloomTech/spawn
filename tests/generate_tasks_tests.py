# multiwindcalc
# Copyright (C) 2018, Simmovation Ltd.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
from os import path
import numpy as np
from multiwindcalc.generate_tasks import generate_tasks_from_spec
from multiwindcalc.tasks.simulation import SimulationTask
from multiwindcalc.plugins.wind.nrel import WindGenerationTask, FastSimulationSpawner
from multiwindcalc.parsers import *


def test_can_create_1d_set_of_aeroelastic_tasks(tmpdir, spawner):
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


def test_can_create_runs_from_tree_spec(tmpdir, spawner, example_data_folder):
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
        assert 'wind_direction' in t.metadata or 'rotor_azimuth' in t.metadata
        seeds.append(t.metadata['turbulence_seed'])
    assert len(seeds) == len(set(seeds))  # testing uniqueness
