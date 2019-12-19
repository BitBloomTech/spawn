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
import pytest
from os import path
import copy

from spawn.simulation_inputs.json import JsonSimulationInput


@pytest.fixture()
def params():
    return {
        'a': 3,
        'b': {
            'c': 'egg',
            'd': 'tadpole'
        }
    }


def test_set_get(params):
    inp = JsonSimulationInput(params)
    inp['a'] = 4
    assert 4 == inp['a']


def test_write_read_round_trip(tmpdir, params):
    inp = JsonSimulationInput(params, indent=2)
    fp = path.join(tmpdir, 'file.json')
    inp.to_file(fp)
    inp2 = JsonSimulationInput.from_file(fp)
    assert params['a'] == inp2['a']
    assert params['b']['c'] == inp2['b']['c']
    assert params['b']['d'] == inp2['b']['d']


def test_deepcopy_unlinks_inputs(params):
    a = JsonSimulationInput(params)
    b = copy.deepcopy(a)
    b['a'] = 5
    a['b']['c'] = 'frog'
    assert params['a'] == a['a']
    assert params['b']['c'] == b['b']['c']


def test_hash_is_same_for_same_inputs(params):
    a = JsonSimulationInput(params)
    b = JsonSimulationInput(params)
    assert a.hash() == b.hash()


def test_hash_is_different_for_diferent_inputs(params):
    a = JsonSimulationInput(params)
    params['b']['d'] = 'frog'
    b = JsonSimulationInput(params)
    assert a.hash() != b.hash()
