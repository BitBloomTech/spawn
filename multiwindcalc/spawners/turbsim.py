from os import path, getcwd
import copy

from multiwindcalc.spawners.wind_generation import WindGenerationSpawner
from .directory_handler import DirectoryHandler
from multiwindcalc.tasks.simulation import WindGenerationTask


class TurbsimSpawner(WindGenerationSpawner):
    """Spawns TurbSim wind generation tasks"""

    def __init__(self, directory, turbsim_input, turbsim_exe, working_dir=None):
        self._directory = directory if isinstance(directory, DirectoryHandler) else DirectoryHandler(directory)
        self._input = turbsim_input
        self._executable = turbsim_exe
        self._working_dir = working_dir if working_dir is not None else getcwd()

    def spawn(self, additional_folder=False):
        directory = self._directory.branch() if additional_folder else self._directory
        wind_input_file = path.join(directory.abspath, 'wind.ipt')
        self._input.to_file(wind_input_file)
        wind_task = WindGenerationTask('wind ' + directory.relative_path, self._executable,
                                       wind_input_file, _working_dir=self._working_dir)
        return wind_task

    def branch(self, branch_id=None):
        branched_spawner = copy.copy(self)
        branched_spawner._directory = self._directory.branch(branch_id)
        branched_spawner._input = copy.deepcopy(self._input)
        return branched_spawner

    def get_simulation_time(self):
        return self._input['AnalysisTime']

    def set_simulation_time(self, time):
        self._input['AnalysisTime'] = time

    def get_wind_speed(self):
        return float(self._input['URef'])

    def set_wind_speed(self, value):
        self._input['URef'] = value

    def get_turbulence_intensity(self):
        """Turbulence intensity as a fraction (not %): ratio of wind speed standard deviation to mean wind speed"""
        return float(self._input['IECturbc']) / 100

    def set_turbulence_intensity(self, turbulence_intensity):
        self._input['IECturbc'] = turbulence_intensity * 100

    def get_turbulence_seed(self):
        """Random number seed for turbulence generation"""
        return int(self._input['RandSeed1'])

    def set_turbulence_seed(self, seed):
        self._input['RandSeed1'] = seed

    def get_wind_shear(self):
        """Vertical wind shear exponent"""
        exponent = self._input['PLExp']
        return float('NaN') if exponent == 'default' else float(exponent)

    def set_wind_shear(self, exponent):
        self._input['PLExp'] = exponent

    def get_upflow(self):
        """Wind inclination in degrees from the horizontal"""
        return float(self._input['VFlowAng'])

    def set_upflow(self, angle):
        self._input['VFlowAng'] = angle