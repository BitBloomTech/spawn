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
"""Defines the :mod:`mutliwindcalc` plugin for nrel
"""
from os import path

from luigi import configuration

from multiwindcalc.util.validation import validate_file

from .simulation_input import TurbsimInput, FastInput
from .turbsim_spawner import TurbsimSpawner
from .fast_spawner import FastSimulationSpawner
from .tasks import WindGenerationTask, FastSimulationTask

def create_spawner(turbsim_exe, fast_exe, turbsim_base_file, fast_base_file, runner_type, outdir, prereq_outdir):
    """Creates an nrel spawner
    """
    validate_file(turbsim_exe, 'turbsim_exe')
    validate_file(fast_exe, 'fast_exe')
    validate_file(turbsim_base_file, 'turbsim_base_file')
    validate_file(fast_base_file, 'fast_base_file')

    luigi_config = configuration.get_config()

    luigi_config.set(WindGenerationTask.__name__, '_exe_path', turbsim_exe)
    luigi_config.set(WindGenerationTask.__name__, '_runner_type', runner_type)
    luigi_config.set(FastSimulationTask.__name__, '_exe_path', fast_exe)
    luigi_config.set(FastSimulationTask.__name__, '_runner_type', runner_type)

    wind_spawner = TurbsimSpawner(TurbsimInput.from_file(turbsim_base_file))
    return FastSimulationSpawner(FastInput.from_file(fast_base_file), wind_spawner, path.join(outdir, prereq_outdir))
