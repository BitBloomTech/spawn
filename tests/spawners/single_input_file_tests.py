# spawn
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
from os import path, mkdir
import json

import pytest
from luigi import configuration

from spawn.spawners import SingleInputFileSpawner
from spawn.simulation_inputs import JsonSimulationInput
from spawn.tasks import SimulationTask


@pytest.fixture()
def sim_input():
    params = {
        'a': 'tadpole',
        'b': {
            'c': 'egg',
            'd': 'frog'
        }
    }
    return JsonSimulationInput(params)


@pytest.fixture(scope='module')
def set_config():
    luigi_config = configuration.get_config()
    luigi_config.set(SimulationTask.__name__, '_runner_type', 'process')
    luigi_config.set(SimulationTask.__name__, '_exe_path', '')


def test_spawn_writes_input_file(sim_input, tmpdir, set_config):
    spawner = SingleInputFileSpawner(sim_input, 'input.json')
    spawner.spawn(tmpdir, {})
    with open(path.join(tmpdir, 'input.json'), 'r') as fp:
        params = json.load(fp)
    assert params['a'] == 'tadpole'


def test_branched_spawner_spawns_different_file(sim_input, tmpdir, set_config):
    spawner = SingleInputFileSpawner(sim_input, 'input.json')
    branch = spawner.branch()
    branch.a = 'frog'
    mkdir(path.join(tmpdir, 'a'))
    mkdir(path.join(tmpdir, 'b'))
    spawner.spawn(path.join(tmpdir, 'a'), {})
    branch.spawn(path.join(tmpdir, 'b'), {})
    with open(path.join(tmpdir, 'a', 'input.json'), 'r') as fp:
        a = json.load(fp)
    with open(path.join(tmpdir, 'b', 'input.json'), 'r') as fp:
        b = json.load(fp)
    assert a != b
    assert b['a'] == 'frog'
