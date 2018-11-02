from enum import Enum

from .process_runner import ProcessRunner
from multiwindcalc.util.validation import validate_type

class RunnerFactory:
    def create(self, runner_type, id_, input_file, *args, **kwargs):
        if runner_type == 'process':
            return ProcessRunner(id_, input_file, *args, **kwargs)
        raise ValueError('Could not create runner of type {}'.format(runner_type))
