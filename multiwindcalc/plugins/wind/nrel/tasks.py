"""NREL Tasks
"""
from os import path

import luigi

from multiwindcalc.tasks import SimulationTask

class WindGenerationTask(SimulationTask):
    """Implementation of :class:`SimulationTask` for TurbSim
    """
    def output(self):
        """The output of this task

        :returns: Target to the .wnd path
        :rtype: :class:`luigi.LocalTarget`
        """
        return luigi.LocalTarget(self.wind_file_path)

    @property
    def wind_file_path(self):
        """The path to the wind file
        """
        return super().run_name_with_path + '.wnd'

class FastSimulationTask(SimulationTask):
    """Implementation of :class:`SimulationTask` for FAST
    """
    def output(self):
        """The output of this task

        :returns: Target to the .outb path
        :rtype: :class:`luigi.LocalTarget`
        """
        run_name_with_path = path.splitext(super().run_name_with_path)[0]
        output = run_name_with_path + '.outb'
        return luigi.LocalTarget(output)
