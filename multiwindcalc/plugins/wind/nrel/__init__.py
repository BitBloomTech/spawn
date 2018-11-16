"""Defines the NREL Wind Plugin for :mod:`multiwindcalc`
"""
from .fast_spawner import FastSimulationSpawner
from .turbsim_spawner import TurbsimSpawner
from .tasks import WindGenerationTask, FastSimulationTask
from .simulation_input import NRELSimulationInput, AerodynInput, FastInput, TurbsimInput
