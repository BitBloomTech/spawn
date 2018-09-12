import os
from os import path
import copy
from multiwindcalc.simulation_inputs.nrel_simulation_input import AerodynInput
from multiwindcalc.run_generator.tasks import FastSimulationTask, WindGenerationTask
from multiwindcalc.run_generator.task_spawner import TaskSpawner, AeroelasticSimulationSpawner
from multiwindcalc.run_generator.directory_handler import DirectoryHandler


def quote(strpath):
    if strpath[0] != '"' or strpath[-1] != '"':
        return '"' + strpath + '"'


class TurbsimSpawner(TaskSpawner):
    """Spawns TurbSim wind generation tasks"""

    def __init__(self, directory, turbsim_input, turbsim_exe, working_dir=None):
        self._directory = directory if isinstance(directory, DirectoryHandler) else DirectoryHandler(directory)
        self._input = turbsim_input
        self._executable = turbsim_exe
        self._working_dir = working_dir if working_dir is not None else os.getcwd()

    def spawn(self):
        wind_input_file = path.join(self._directory.abspath, 'wind.ipt')
        self._input.to_file(wind_input_file)
        wind_task = WindGenerationTask('wind ' + self._directory.relative_path, self._executable,
                                       wind_input_file, _working_dir=self._working_dir)
        return wind_task

    def branch(self, branch_id=None):
        branched_spawner = copy.copy(self)
        branched_spawner._directory = self._directory.branch(branch_id)
        branched_spawner._input = copy.deepcopy(self._input)
        return branched_spawner

    @property
    def wind_speed(self):
        return self._input['URef']

    @wind_speed.setter
    def wind_speed(self, value):
        self._input['URef'] = value

    @property
    def simulation_time(self):
        return self._input['AnalysisTime']

    @simulation_time.setter
    def simulation_time(self, time):
        self._input['AnalysisTime'] = time


class FastSimulationSpawner(AeroelasticSimulationSpawner):
    """Spawns FAST simulation tasks with wind generation dependency if necessary"""

    def __init__(self, directory, fast_input, fast_exe, wind_spawner, working_dir=None):
        self._directory = directory if isinstance(directory, DirectoryHandler) else DirectoryHandler(directory)
        self._input = fast_input
        self._executable = fast_exe
        self._wind_spawner = wind_spawner
        self._working_dir = working_dir if working_dir is not None else os.getcwd()
        # non-arguments:
        self._aerodyn_input = AerodynInput.from_file(self._input['ADFile'])
        self._wind_environment_changed = False
        self._wind_task = None

    def spawn(self):
        preproc_tasks = self._spawn_preproc_tasks()
        sim_input_file = path.join(self._directory.abspath, 'simulation.ipt')
        self._input.to_file(sim_input_file)
        sim_task = FastSimulationTask('run ' + self._directory.relative_path,
                                      self._executable,
                                      sim_input_file,
                                      preproc_tasks,
                                      _working_dir=self._working_dir)
        return sim_task

    def _spawn_preproc_tasks(self):
        preproc_tasks = []
        # Generate new wind file if needed
        if self._wind_environment_changed:
            self._wind_task = self._wind_spawner.spawn()
            self._aerodyn_input['WindFile'] = quote(self._wind_task.wind_file_path)
            aerodyn_file_path = path.join(self._directory.abspath, 'aerodyn.ipt')
            self._aerodyn_input.to_file(aerodyn_file_path)
            self._input['ADFile'] = quote(aerodyn_file_path)
            self._wind_environment_changed = False
        return [self._wind_task] if self._wind_task is not None else []

    def branch(self, branch_id=None):
        branched_spawner = copy.copy(self)
        branched_spawner._directory = self._directory.branch(branch_id)
        branched_spawner._input = copy.deepcopy(self._input)
        branched_spawner._wind_spawner = self._wind_spawner.branch(branch_id)
        return branched_spawner

    # Properties in FAST input file
    @property
    def output_start_time(self):
        return float(self._input['TStart'])

    @output_start_time.setter
    def output_start_time(self, time):
        self._input['TStart'] = time

    @property
    def simulation_time(self):
        """Total simulation time in seconds"""
        return float(self._input['TMax'])

    @simulation_time.setter
    def simulation_time(self, time):
        self._input['TMax'] = time
        self._wind_spawner.simulation_time = time

    # Properties deferred to wind generation spawner:
    @property
    def wind_speed(self):
        """Mean wind speed in m/s"""
        return float(self._wind_spawner.wind_speed)

    @wind_speed.setter
    def wind_speed(self, speed):
        self._wind_spawner.wind_speed = speed
        self._wind_environment_changed = True

