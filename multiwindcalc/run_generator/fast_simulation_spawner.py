import os
from os import path
import copy
from multiwindcalc.simulation_inputs.nrel_simulation_input import AerodynInput
from multiwindcalc.run_generator.tasks import FastSimulationTask, WindGenerationTask
from multiwindcalc.run_generator.task_spawner import TaskSpawner, AeroelasticSimulationSpawner
from multiwindcalc.run_generator.directory_handler import DirectoryHandler


class TurbsimSpawner(TaskSpawner):
    def __init__(self, directory, turbsim_input, turbsim_exe, working_dir=os.getcwd()):
        self._directory = directory if isinstance(directory, DirectoryHandler) else DirectoryHandler(directory)
        self._input = turbsim_input
        self._executable = turbsim_exe
        self._working_dir = working_dir

    def spawn(self):
        wind_input_file = path.join(self._directory.abspath, 'wind.ipt')
        self._input.to_file(wind_input_file)
        wind_task = WindGenerationTask('wind ' + self._directory.relative_path, self._executable,
                                       wind_input_file, _working_dir=self._working_dir)
        return wind_task

    def branch(self, branch_id=None):
        return TurbsimSpawner(self._directory.branch(branch_id), copy.deepcopy(self._input), self._executable,
                              self._working_dir)

    @property
    def wind_speed(self):
        return self._input['URef']

    @wind_speed.setter
    def wind_speed(self, value):
        self._input['URef'] = value


class FastSimulationSpawner(AeroelasticSimulationSpawner):
    def __init__(self, directory, fast_input, fast_exe, wind_spawner, working_dir=os.getcwd()):
        self._directory = directory if isinstance(directory, DirectoryHandler) else DirectoryHandler(directory)
        self._input = fast_input
        self._executable = fast_exe
        self._wind_spawner = wind_spawner
        self._working_dir = working_dir
        # non-arguments:
        self._aerodyn_input = AerodynInput.from_file(self._input['ADFile'])
        self._wind_environment_changed = False

    def spawn(self):
        self._aerodyn_input.to_file(path.join(self._directory.abspath, 'aerodyn.ipt'))
        sim_input_file = path.join(self._directory.abspath, 'simulation.ipt')
        self._input.to_file(sim_input_file)
        sim_task = FastSimulationTask('run ' + self._directory.relative_path,
                                      self._executable,
                                      sim_input_file,
                                      self._spawn_preproc_tasks(),
                                      _working_dir=self._working_dir)
        return sim_task

    def _spawn_preproc_tasks(self):
        preproc_tasks = []
        # Generate new wind file if needed
        if self._wind_environment_changed:
            wind_task = self._wind_spawner.spawn()
            self._aerodyn_input['WindFile'] = wind_task.wind_file_path
            self._wind_environment_changed = False
            preproc_tasks.append(wind_task)
        return preproc_tasks

    def branch(self, branch_id=None):
        return FastSimulationSpawner(self._directory.branch(branch_id), copy.deepcopy(self._input), self._executable,
                                     self._wind_spawner.branch(branch_id), self._working_dir)

    # Properties in FAST input file
    @property
    def simulation_time(self):
        return self._input['TMax']

    @simulation_time.setter
    def simulation_time(self, time):
        self._input['TMax'] = time

    # Properties deferred to wind generation spawner:
    @property
    def wind_speed(self):
        return self._wind_spawner.wind_speed

    @wind_speed.setter
    def wind_speed(self, speed):
        self._wind_spawner.wind_speed = speed
        self._wind_environment_changed = True

