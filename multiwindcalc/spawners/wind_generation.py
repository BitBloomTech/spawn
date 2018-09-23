from .task_spawner import TaskSpawner


class WindGenerationSpawner(TaskSpawner):
    """Base class for spawning wind generation tasks"""

    @property
    def simulation_time(self):
        raise NotImplementedError()

    @simulation_time.setter
    def simulation_time(self, time):
        raise NotImplementedError()

    @property
    def wind_speed(self):
        raise NotImplementedError()

    @wind_speed.setter
    def wind_speed(self, value):
        raise NotImplementedError()

    @property
    def turbulence_intensity(self):
        """Turbulence intensity as a fraction (not %): ratio of wind speed standard deviation to mean wind speed"""
        raise NotImplementedError()

    @turbulence_intensity.setter
    def turbulence_intensity(self, turbulence_intensity):
        raise NotImplementedError()

    @property
    def turbulence_seed(self):
        """Random number seed for turbulence generation"""
        raise NotImplementedError()

    @turbulence_seed.setter
    def turbulence_seed(self, seed):
        raise NotImplementedError()

    @property
    def wind_shear(self):
        """Vertical wind shear exponent"""
        raise NotImplementedError()

    @wind_shear.setter
    def wind_shear(self, exponent):
        raise NotImplementedError()

    @property
    def upflow(self):
        """Wind inclination in degrees from the horizontal"""
        raise NotImplementedError()

    @upflow.setter
    def upflow(self, angle):
        raise NotImplementedError()
