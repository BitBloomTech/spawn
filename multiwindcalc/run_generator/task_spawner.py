

class TaskSpawner:
    """Base class task spawner"""

    def spawn(self):
        """Create new derivative of luigi.Task for later execution"""
        raise NotImplementedError

    def branch(self, branch_id=None):
        """Deep copy task input and dependencies so that they can be edited without affecting trunk object"""
        raise NotImplementedError


class AeroelasticSimulationSpawner:
    """Spawner of aeroelastic simulations of wind turbines including pre-processing dependencies"""

    @property
    def output_start_time(self):
        raise NotImplementedError

    @output_start_time.setter
    def output_start_time(self, time):
        raise NotImplementedError

    @property
    def simulation_time(self):
        """Total simulation time in seconds"""
        raise NotImplementedError

    @simulation_time.setter
    def simulation_time(self):
        raise NotImplementedError

    @property
    def wind_speed(self):
        """Mean wind speed in m/s"""
        raise NotImplementedError

    @wind_speed.setter
    def wind_speed(self, wind_speed):
        raise NotImplementedError
