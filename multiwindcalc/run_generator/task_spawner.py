import os
from os import path
from multiwindcalc.run_generator.directory_handler import DirectoryHandler
from multiwindcalc.run_generator.tasks import FastSimulationTask, WindGenerationTask


class FastTaskSpawner:
    def __init__(self, base_output_path,
                 input_editor, wind_input_editor,
                 simulation_exe, wind_generation_exe,
                 working_dir=os.getcwd()):
        self._wind_dirs = DirectoryHandler(path.join(base_output_path, 'wind'))
        self._runs_dirs = DirectoryHandler(path.join(base_output_path, 'runs'))
        self._runs_editor = input_editor
        self._wind_editor = wind_input_editor
        self._simulation_exe = simulation_exe
        self._wind_generation_exe = wind_generation_exe
        self._working_dir = working_dir

    def spawn(self, editions):
        if self._runs_editor.changes_wind_environment(editions):
            self._wind_dirs.make_new_dir()
            wind_input_file = path.join(self._wind_dirs.abspath, 'wind.ipt')
            self._wind_editor.write(wind_input_file, editions)
            wind_task = WindGenerationTask('wind ' + self._wind_dirs.relative_path,
                                           self._wind_generation_exe,
                                           wind_input_file,
                                           _working_dir=self._working_dir)
            editions['wind_file'] = wind_task.wind_file_path
        self._runs_dirs.make_new_dir()
        sim_input_file = path.join(self._runs_dirs.abspath, 'simulation.ipt')
        self._runs_editor.write(sim_input_file, editions)
        sim_task = FastSimulationTask('run ' + self._runs_dirs.relative_path,
                                      self._simulation_exe,
                                      sim_input_file,
                                      wind_task,
                                      _working_dir=self._working_dir)
        return sim_task

