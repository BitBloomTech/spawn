"""Task Spawners for ``multiwindcalc``

Task spawners turn specification nodes into tasks that can be submitted by a scheduler
"""
from .task_spawner import TaskSpawner
from .aeroelastic_simulation import AeroelasticSimulationSpawner
from .fast_simulation import FastSimulationSpawner
from .wind_generation import WindGenerationSpawner
from .turbsim import TurbsimSpawner
