import queue
import subprocess
import os.path as path


def write_logs(run_name, output):
    with open(run_name + '.log', 'wb') as fp:
        fp.write(output.stdout)
    if output.stderr:
        with open(run_name + '.err', 'wb') as fp:
            fp.write(output.stderr)


class Batch:
    def __init__(self, working_dir):
        self._runs = queue.Queue()
        self._working_dir = working_dir

    def add_run(self, run_id, executable, input_file_path):
        self._runs.put({'run_id': run_id, 'executable': executable, 'input_file_path': input_file_path})

    def execute(self):
        n_runs = self._runs.qsize()
        print('Batch executing {} runs'.format(n_runs))
        runs_done = 0
        while not self._runs.empty():
            run = self._runs.get()
            args = [run['executable'], run['input_file_path']]
            print('Executing \'{}\''.format(run['run_id']))
            output = subprocess.run(args=args, cwd=self._working_dir,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            write_logs(path.splitext(run['input_file_path'])[0], output)
            runs_done += 1
            print('{:.1%}'.format(runs_done / n_runs))
