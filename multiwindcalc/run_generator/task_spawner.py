

class TaskSpawner:
    def spawn(self):
        raise NotImplementedError

    def branch(self):
        raise NotImplementedError


class AeroelasticSimulationSpawner:
    @property
    def wind_speed(self):
        raise NotImplementedError

    @wind_speed.setter
    def wind_speed(self, wind_speed):
        raise NotImplementedError
