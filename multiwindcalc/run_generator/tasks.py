import subprocess
import os
from os import path
import logging
import luigi

LOGGER = logging.getLogger(__name__)

class SimulationTask(luigi.Task):
    _id = luigi.Parameter()
    _executable_path = luigi.Parameter()
    _input_file_path = luigi.Parameter()
    _dependencies = luigi.Parameter(default=[])
    _working_dir = luigi.Parameter(default=os.getcwd())
    _complete = False

    def requires(self):
        return self._dependencies

    def run(self):
        args = [self._executable_path, self._input_file_path]
        LOGGER.info('Executing \'{}\''.format(self._id))
        output = subprocess.run(args=args, cwd=self._working_dir,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._write_logs(output)
        self._complete = True
        if output.returncode != 0:
            raise ChildProcessError('process exited with {}'.format(output.returncode))

    def complete(self):
        return self._complete

    def _write_logs(self, output):
        run_name = path.splitext(self._input_file_path)[0]
        with open(run_name + '.log', 'wb') as fp:
            fp.write(output.stdout)
        if output.stderr:
            with open(run_name + '.err', 'wb') as fp:
                fp.write(output.stderr)
        elif output.returncode != 0:
            with open(run_name + '.err', 'w') as fp:
                fp.write(str(output.returncode))

    @property
    def run_name_with_path(self):
        return path.splitext(self._input_file_path)[0]


class WindGenerationTask(SimulationTask):
    def output(self):
        run_name_with_path = path.splitext(super().run_name_with_path)[0]
        output = run_name_with_path + '.wnd'
        return luigi.LocalTarget(output)

    @property
    def wind_file_path(self):
        return super().run_name_with_path + '.wnd'


class FastSimulationTask(SimulationTask):
    def output(self):
        run_name_with_path = path.splitext(super().run_name_with_path)[0]
        output = run_name_with_path + '.outb'
        return luigi.LocalTarget(output)
