"""luigi Tasks
"""
import subprocess
import os
from os import path
import logging
import luigi
import json

from multiwindcalc.runners import RunnerFactory

LOGGER = logging.getLogger(__name__)

class TaskListParameter(luigi.Parameter):
    """Implementation of :class:`luigi.Parameter` to allow definitions of multiple tasks as dependencies
    """
    def parse(self, input):
        input_strings = json.loads(input)
        return [luigi.task_register.Register.get_task_cls(i) for i in input_strings]
    
    def serialize(self, clss):
        return json.dumps([cls.get_task_family() for cls in clss])

class SimulationTask(luigi.Task):
    """Implementation of :class:`luigi.Task`
    """
    _id = luigi.Parameter()
    _input_file_path = luigi.Parameter()
    _runner_type = luigi.Parameter()
    _metadata = luigi.DictParameter(default={})
    _runner_type = luigi.Parameter()
    _exe_path = luigi.Parameter()

    def run(self):
        """Run this task
        """
        self._create_runner().run()
    
    def complete(self):
        """Determine if this task is complete

        :returns: ``True`` if this task is complete; otherwise ``False``
        :rtype: bool
        """
        return self._create_runner().complete()

    @property
    def run_name_with_path(self):
        """Return the run name of this task
        """
        return path.splitext(self._input_file_path)[0]

    @property
    def metadata(self):
        """Metadata for this task
        """
        return self._metadata

    def _create_runner(self):
        return RunnerFactory().create(self._runner_type, self._id, self._input_file_path, exe_path=self._exe_path)

class WindGenerationTask(SimulationTask):
    """Implementation of :class:`SimulationTask` for TurbSim
    """
    def output(self):
        """The output of this task

        :returns: Target to the .wnd path
        :rtype: :class:`luigi.LocalTarget`
        """
        run_name_with_path = path.splitext(super().run_name_with_path)[0]
        output = run_name_with_path + '.wnd'
        return luigi.LocalTarget(output)

    @property
    def wind_file_path(self):
        """The path to the wind file
        """
        return super().run_name_with_path + '.wnd'

class FastSimulationTask(SimulationTask):
    """Implementation of :class:`SimulationTask` for FAST
    """
    _dependencies = TaskListParameter(default=[])

    def output(self):
        """The output of this task

        :returns: Target to the .outb path
        :rtype: :class:`luigi.LocalTarget`
        """
        run_name_with_path = path.splitext(super().run_name_with_path)[0]
        output = run_name_with_path + '.outb'
        return luigi.LocalTarget(output)

    def requires(self):
        """The prerequisites for this task
        """
        return self._dependencies