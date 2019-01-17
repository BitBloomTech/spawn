# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
"""Implementation of the :class:`ProcessRunner`
"""
import subprocess
import logging
from os import path, getcwd
import json

from spawn.util.validation import validate_file

LOGGER = logging.getLogger(__name__)

SUCCESS = 'success'
FAILURE = 'failure'

class ProcessRunner:
    """Runner that uses the native os process (provided by :mod:`subprocess`) in order to run tasks
    """
    def __init__(self, id_, input_file_path, exe_path, run_name=None, output_dir=None, cwd=None):
        """Initialises the :class:`ProcessRunner`

        :param id_: The ID of the runner
        :type id_: str
        :param input_file_path: The path to the input file
        :type input_file_path: path-like
        :param exe_path: The path to the executable
        :type exe_path: path-like
        :param run_name: The name of the run. Defaults to the base name of the input file path.
        :type run_name: str
        :param output_dir: The output directory for the run. Defaults to the directory of the input file.
        :type output_dir: path-like
        :param cwd: The current working directory for the child process.
            Defaults to the current working directory for the parent process.
        :type cwd: path-like
        """
        self._id = id_
        self._input_file_path = input_file_path
        self._exe_path = exe_path
        self._run_name = run_name or path.splitext(path.basename(input_file_path))[0]
        self._output_dir = output_dir or path.dirname(input_file_path)
        self._cwd = cwd or getcwd()

    def run(self):
        """Runs the process synchronously.

        Runs the process synchronously and when complete writes the log files and a status file.
        """
        validate_file(self._input_file_path, 'input_file_path')
        validate_file(self._exe_path, 'exe_path')
        LOGGER.info('Executing \'%s\': %s', self._id, self.process_args)
        output = subprocess.run(args=self.process_args, cwd=self._cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._write_logs(output)
        state = self._output_to_state(output)
        with open(self.state_file, 'w') as fp:
            json.dump(state, fp)
        if output.returncode != 0:
            raise ChildProcessError('process exited with {}'.format(output.returncode))

    def error_logs(self):
        """Error logs produced by the process, if any

        :returns: The output written to stderr, if any, otherwise ``None``
        :rtype: str
        """
        error_file = self.output_file_base + '.err'
        if path.isfile(error_file):
            with open(error_file) as fp:
                return fp.read()
        return None

    def logs(self):
        """Stdout logs produced by the process, if any

        :returns: The output written to stdout, if any, otherwise ``None``
        :rtype: str
        """
        log_file = self.output_file_base + '.log'
        if path.isfile(log_file):
            with open(log_file) as fp:
                return fp.read()
        return None

    def complete(self):
        """Determine if the run is complete.

        :returns: ``True`` if the run is complete; ``False`` otherwise.
        :rtype: bool
        """
        if path.isfile(self.output_file_base + '.state.json'):
            with open(self.state_file) as fp:
                state = json.load(fp)
            return state['result'] == SUCCESS
        return False

    @property
    def process_args(self):
        """The arguments to be provided to the subprocess.

        Can be overridden in derived classes.

        :returns: An array containing the process arguments
        :rtype: list
        """
        return [self._exe_path, self._input_file_path]

    @property
    def output_file_base(self):
        """The base path of the output file (without extension)

        :returns: The path to the output file, without extension.
        :rtype: path-like
        """
        return path.join(self._output_dir, self._run_name)

    @property
    def state_file(self):
        """The path to the state file

        :returns: The path to the state file
        :rtype: path-like
        """
        return self.output_file_base + '.state.json'

    def _write_logs(self, output):
        with open(self.output_file_base + '.log', 'wb') as fp:
            fp.write(output.stdout)
        if output.stderr:
            with open(self.output_file_base + '.err', 'wb') as fp:
                fp.write(output.stderr)
        elif output.returncode != 0:
            with open(self.output_file_base + '.err', 'w') as fp:
                fp.write(str(output.returncode))

    @staticmethod
    def _output_to_state(output):
        return {
            'result': SUCCESS if output.returncode == 0 else FAILURE,
            'returncode': output.returncode
        }
