"""Defines the wind generation spawners
"""
from multiwindcalc.util import FloatProperty, IntProperty

from .task_spawner import TaskSpawner


class WindGenerationSpawner(TaskSpawner):
    """Base class for spawning wind generation tasks"""

    simulation_time = FloatProperty(abstract=True)
    wind_speed = FloatProperty(abstract=True)
    turbulence_intensity = FloatProperty(doc='Turbulence intensity as a fraction (not %): ratio of wind speed standard deviation to mean wind speed', abstract=True)
    turbulence_seed = IntProperty(doc='Random number seed for turbulence generation', abstract=True)
    wind_shear = FloatProperty(doc='Vertical wind shear exponent', abstract=True)
    upflow = FloatProperty(doc='Wind inclination in degrees from the horizontal', abstract=True)
