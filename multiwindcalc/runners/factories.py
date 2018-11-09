"""Factory methods for runners
"""
from enum import Enum

from .process_runner import ProcessRunner
from multiwindcalc.util.validation import validate_type

class RunnerFactory:
    """Factory to create runners
    """
    def create(self, runner_type, id_, input_file, *args, **kwargs):
        """Creates runners

        Given a specified ``runner_type``, returns a runner object of the correct type.

        :param runner_type: The type of runner to initialise
        :type runner_type: str
        :param id_: The ID of the runner to create
        :type id_: str
        :param input_file: The input file for the runner
        :type input_file: path-like
        :returns: The correct runner
        :rtype: Runner
        """
        if runner_type == 'process':
            return ProcessRunner(id_, input_file, *args, **kwargs)
        raise ValueError('Could not create runner of type {}'.format(runner_type))
