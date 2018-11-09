"""Implementation of :class:`TaskSpawner` for aeroelastic simulations
"""
from .task_spawner import TaskSpawner

from multiwindcalc.util import StringProperty, IntProperty, FloatProperty


class AeroelasticSimulationSpawner(TaskSpawner):
    """Spawner of aeroelastic simulations of wind turbines including pre-processing dependencies"""

    # Simulation options
    output_start_time = FloatProperty(abstract=True)
    simulation_time = FloatProperty(doc='Total simulation time in seconds', abstract=True)
    operation_mode = StringProperty(
        possible_values=['normal', 'idling', 'parked'],
        doc="""Operation mode:
        'normal' - power production run with generator on and rotor free
        'idling' - generator off but rotor free
        'parked' - generator off and rotor fixed
        """,
        abstract=True
    )
    initial_rotor_speed = FloatProperty(doc='Rotor speed at start of simulation in rpm', abstract=True)
    initial_azimuth = FloatProperty(doc='Rotor azimuth of blade 1 at start of simulation in degrees', abstract=True)
    initial_yaw_angle = FloatProperty(doc='Nacelle yaw angle at start of simulation in degrees; clockwise from North', abstract=True)
    initial_pitch_angle = FloatProperty(doc='Sets pitch angle for all blades at start of simulation; in degrees, positive towards feather', abstract=True)

    # Wind properties
    wind_speed = FloatProperty(doc='Mean wind speed in m/s', abstract=True)
    turbulence_intensity = FloatProperty(doc='Turbulence intensity as a fraction (not %): ratio of wind speed standard deviation to mean wind speed', abstract=True)
    turbulence_seed = IntProperty(doc='Random number seed for turbulence generation', abstract=True)
    wind_shear = FloatProperty(doc='Vertical wind shear exponent', abstract=True)
    upflow = FloatProperty(doc='Wind inclination in degrees from the horizontal, abstract=True')

    # Properties of turbine, for which setting is not supported
    number_of_blades = IntProperty(readonly=True, abstract=True)
