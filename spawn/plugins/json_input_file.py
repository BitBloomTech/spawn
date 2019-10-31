# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
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
"""Plugin for running tasks that take a single JSON input file as command line argument
"""
import json
import logging

from luigi import configuration

from ..util.validation import validate_file, validate_dir
from ..spawners import SingleInputFileSpawner
from ..tasks import SimulationTask
from ..simulation_inputs import JsonSimulationInput


def create_spawner(task_exe, working_dir, base_file, runner_type):
    """
    Creates spawner that creates tasks taking a single JSON input file as command line argument

    :param task_exe: Path of executable to run. If None, input files will be written but no tasks run
    :param working_dir: Working directory of task execution
    :param base_file: Baseline JSON file on which to make parameter editions and additions. If None, parameter additions
     will be made onto an empty input
    :return: :class:`SingleInputFileSpawner` object
    """
    if task_exe is not None:
        validate_file(task_exe, 'task_exe')
    if working_dir is not None:
        validate_dir(working_dir, 'working_dir')
    if base_file is not None:
        validate_file(base_file, 'base_file')

    if task_exe is None:
        task_exe = ''
    if working_dir is None:
        working_dir = '.'

    logger = logging.getLogger(__name__)
    logger.info("Creating Single input file spawner with JSON input")
    logger.info("task_exe = %s", task_exe)
    logger.info("working_dir = %s", working_dir)
    logger.info("base_file = %s", base_file)
    logger.info("runner_type = %s", runner_type)

    luigi_config = configuration.get_config()
    luigi_config.set(SimulationTask.__name__, '_exe_path', task_exe)
    luigi_config.set(SimulationTask.__name__, '_working_dir', working_dir)
    luigi_config.set(SimulationTask.__name__, '_runner_type', runner_type)

    if base_file is not None:
        with open(base_file, 'r') as fp:
            params = json.load(fp)
    else:
        params = {}
    sim_input = JsonSimulationInput(params, indent=2)
    return SingleInputFileSpawner(sim_input, 'input.json')
