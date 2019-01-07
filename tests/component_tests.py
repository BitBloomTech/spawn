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
from spawn.generate_tasks import generate_tasks_from_spec
from spawn.parsers.specification_parser import SpecificationNodeParser
from spawn.parsers.value_proxy import ValueProxyParser


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
