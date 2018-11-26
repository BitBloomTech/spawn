"""Defines the turbsim spawner
"""
from os import path, getcwd, makedirs
import copy

from multiwindcalc.plugins.wind import WindGenerationSpawner
from .tasks import WindGenerationTask


class TurbsimSpawner(WindGenerationSpawner):
    """Spawns TurbSim wind generation tasks"""

    def __init__(self, turbsim_input):
        self._input = turbsim_input

    def spawn(self, path_, metadata):
        if not path.isdir(path_):
            makedirs(path_)
        wind_input_file = path.join(path_, 'wind.ipt')
        self._input.to_file(wind_input_file)
        wind_task = WindGenerationTask('wind ' + path_, wind_input_file, _metadata=metadata)
        return wind_task

    def branch(self):
        branched_spawner = copy.copy(self)
        branched_spawner._input = copy.deepcopy(self._input)
        return branched_spawner

    def get_duration(self):
        return float(self._input['UsableTime'])

    def set_duration(self, duration):
        self._input['UsableTime'] = duration

    def get_analysis_time(self):
        return self._input['AnalysisTime']

    def set_analysis_time(self, time):
        self._input['AnalysisTime'] = time

    def get_wind_speed(self):
        return float(self._input['URef'])

    def set_wind_speed(self, value):
        self._input['URef'] = value

    def get_turbulence_intensity(self):
        return float(self._input['IECturbc'])

    def set_turbulence_intensity(self, turbulence_intensity):
        self._input['IECturbc'] = turbulence_intensity

    def get_turbulence_seed(self):
        return int(self._input['RandSeed1'])

    def set_turbulence_seed(self, seed):
        self._input['RandSeed1'] = seed

    def get_wind_shear(self):
        exponent = self._input['PLExp']
        return float('NaN') if exponent == 'default' else float(exponent)

    def set_wind_shear(self, exponent):
        self._input['PLExp'] = exponent

    def get_upflow(self):
        return float(self._input['VFlowAng'])

    def set_upflow(self, angle):
        self._input['VFlowAng'] = angle