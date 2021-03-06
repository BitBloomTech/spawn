# spawn
# Copyright (C) 2018, Simmovation Ltd.
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
import pytest

from os import path, getcwd
import json

from spawn.runners.process_runner import ProcessRunner

@pytest.fixture
def output(mocker):
    output = mocker.Mock()
    output.stdout = 'output'.encode('utf8')
    output.stderr = 'error'.encode('utf8')
    output.returncode = 0
    return output

@pytest.fixture
def subprocess(mocker, output):
    subprocess_mock = mocker.Mock()
    mocker.patch('spawn.runners.process_runner.subprocess', subprocess_mock)
    subprocess_mock.run.return_value = output
    return subprocess_mock

@pytest.fixture
def input_file(tmpdir):
    input_file = path.join(tmpdir, 'input_file')
    with open(input_file, 'w') as fp:
        fp.write('hello world')
    return input_file

@pytest.fixture
def exe_path(tmpdir):
    exe_path = path.join(tmpdir, 'exe_path')
    with open(exe_path, 'w') as fp:
        fp.write('hello world')
    return exe_path

@pytest.fixture
def runner(input_file, exe_path):
    return ProcessRunner('42', input_file, exe_path)

def test_run_called_with_correct_args(runner, subprocess, exe_path, input_file):
    runner.run()
    _, kwargs = subprocess.run.call_args
    assert kwargs['args'] == [exe_path, input_file]
    assert kwargs['cwd'] == getcwd()

def test_correct_output_files_written(runner, subprocess, tmpdir):
    runner.run()
    log_file = path.join(tmpdir, 'input_file' + '.log')
    assert path.isfile(log_file)
    with open(log_file, 'r') as fp:
        assert fp.read() == 'output'
    err_file = path.join(tmpdir, 'input_file' + '.err')
    assert path.isfile(err_file)
    with open(err_file, 'r') as fp:
        assert fp.read() == 'error'
    success_file = path.join(tmpdir, 'input_file' + '.state.json')
    assert path.isfile(success_file)
    with open(success_file) as fp:
        state = json.load(fp)
    assert state['result'] == 'success'
    assert state['returncode'] == 0

def test_exception_raised_and_state_failure_written_on_non_zero_error_code(runner, subprocess, output, tmpdir):
    output.returncode = 1
    with pytest.raises(ChildProcessError):
        runner.run()
    assert path.isfile(path.join(tmpdir, 'input_file' + '.state.json'))
    with open(path.join(tmpdir, 'input_file' + '.state.json')) as fp:
        state = json.load(fp)
    assert state['result'] == 'failure'
    assert state['returncode'] == 1

def test_ouptut_path_base_defaults_to_input_file_no_extension(runner, tmpdir):
    assert runner.output_file_base == path.join(tmpdir, 'input_file')

def test_logs_returns_output(runner, subprocess, tmpdir):
    runner.run()
    assert runner.logs() == 'output'
    assert runner.error_logs() == 'error'