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

    wind_spawner = TurbsimSpawner(TurbsimInput.from_file(turbsim_base_file), path.join(outdir, prereq_outdir))
    return FastSimulationSpawner(FastInput.from_file(fast_base_file), wind_spawner)
