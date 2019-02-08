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
from os import path, pardir
import luigi
from spawn.tasks.generate import generate_tasks_from_spec
from spawn.parsers.specification_parser import SpecificationNodeParser
from spawn.parsers.value_proxy import ValueProxyParser


def test_can_run_job_with_dependency(spawner, tmpdir):
    spec = {
        "runs": [{'alpha': 8.0, 'beta': 0.0, 'gamma': 1.0}]
    }
    run_spec = {
        'alpha': 8.0, 'beta': 0.0, 'gamma': 1.0
    }
    root_node = SpecificationNodeParser(ValueProxyParser({})).parse(run_spec)
    tasks = generate_tasks_from_spec(spawner, root_node, tmpdir.strpath)
    luigi.build(tasks, local_scheduler=True, log_level='WARNING')
    assert tasks[0].complete()
