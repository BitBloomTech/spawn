"""Defines the wind generation spawners
"""
from multiwindcalc.util import FloatProperty, IntProperty
from multiwindcalc.spawners import TaskSpawner


class WindGenerationSpawner(TaskSpawner):
    """Base class for spawning wind generation tasks"""

    duration = FloatProperty(doc='Duration of the wind file in seconds', abstract=True)
    analysis_time = FloatProperty(doc='Time period in seconds on which the wind statistics are based', abstract=True)
    wind_speed = FloatProperty(doc='Mean wind speed in m/s in the longitudinal direction', abstract=True)
    turbulence_intensity = FloatProperty(doc='Turbulence intensity as a percentage ratio of wind speed standard deviation to mean wind speed', abstract=True)
    turbulence_seed = IntProperty(doc='Random number seed for turbulence generation', abstract=True)
    wind_shear = FloatProperty(doc='Vertical wind shear exponent', abstract=True)
    upflow = FloatProperty(doc='Wind inclination in degrees from the horizontal', abstract=True)
