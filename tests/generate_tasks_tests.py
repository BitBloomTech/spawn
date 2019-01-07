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
from os import path
import numpy as np
from spawn.generate_tasks import generate_tasks_from_spec
from spawn.tasks import SpawnTask
from spawn.parsers import *
from spawn.parsers.value_proxy import ValueProxyParser

from .conftest import *


def test_can_create_1d_set_of_tasks(tmpdir, spawner, run_registry):
    run_spec = {'alpha': list(np.arange(4.0, 15.0, 2.0))}
    root_node = SpecificationNodeParser(ValueProxyParser({})).parse(run_spec)
    tasks = generate_tasks_from_spec(spawner, root_node, tmpdir.strpath)
    assert len(tasks) == 6
    for t in tasks:
        assert isinstance(t, SpawnTask)
        assert len(t.requires()) == 1
        assert isinstance(t.requires()[0], FooTask)
        assert 'alpha' in t.metadata


def test_can_create_runs_from_example_spec(tmpdir, spawner, plugin_loader, example_data_folder):
    input_path = path.join(example_data_folder, 'example_spec.json')
    spec_model = SpecificationParser(SpecificationFileReader(input_path), plugin_loader).parse()
    runs = generate_tasks_from_spec(spawner, spec_model.root_node, tmpdir.strpath)
    assert len(runs) == 3 * (3 + 9*4)
    for t in runs:
        assert isinstance(t, SpawnTask)
        assert len(t.requires()) == 1
        assert isinstance(t.requires()[0], FooTask)
        assert 'alpha' in t.metadata
        assert 'beta' in t.metadata
        assert t.metadata['beta'] in ['egg', 'tadpole', 'frog']
