import os
from os import path
from multiwindcalc.run_generator.run_generator import generate_preprocessing_runs, generate_time_domain_runs
from ..component_tests import example_data_folder


class DummyBatch:
    def __init__(self):
        self.runs = []

    def add_run(self, run_id, executable, input_file_path):
        self.runs.append({'id': run_id, 'executable': executable, 'input_file': input_file_path})


__example_dir = path.join(example_data_folder, 'fast_input_files')


def test_generates_preprocessing():
    spec = {
        'base_wind_input': str(path.join(__example_dir, 'TurbSim.inp')),
        'wind_executable': 'wind.exe',
        'load_cases': [
            {
                'type': 'grid',
                'path': 'a',
                'variables':
                    {
                        'wind_speed': [6.0, 8.0],
                        'turbulence_intensity': [10.0, 12.0]
                    }
            }
        ]
    }
    batch = DummyBatch()
    generate_preprocessing_runs(spec, path.join(os.getcwd(), 'temp'), batch)
    assert(len(batch.runs) == 4)
    assert(spec['load_cases'][0]['type'] == 'list')
    assert(len(spec['load_cases'][0]['variables']) == 4)
    for run in spec['load_cases'][0]['variables']:
        assert('wind_file' in run)
        assert('wind_speed' in run)
        assert('turbulence_intensity' in run)


def test_generates_time_domain_runs():
    spec = {
        'base_time_domain_input': str(path.join(__example_dir, 'NRELOffshrBsline5MW_Onshore.fst')),
        'time_domain_executable': 'C:\\AeroElastic\\FASTv7\\TurbSim\\FASTv7.0.2.exe',
        'load_cases': [
            {
                'type': 'list',
                'path': 'a',
                'variables': [
                    {
                        'wind_speed': 5.0,
                        'turbulence_intensity': 12.0,
                        'wind_file': 'TurbSim_5_12'
                    },
                    {
                        'wind_speed': 6.0,
                        'turbulence_intensity': 14.0,
                        'wind_file': 'TurbSim_6_14'
                    }
                ]
            }
        ]
    }
    batch = DummyBatch()
    generate_time_domain_runs(spec, path.join(os.getcwd(), 'temp'), batch)
    for var in spec['load_cases'][0]['variables']:
        assert '.outb' in var['output']
    assert(len(batch.runs) == 2)
    with open(batch.runs[0]['input_file']) as fp:
        file1 = fp.read()
    with open(batch.runs[1]['input_file']) as fp:
        file2 = fp.read()
    assert file1 == file2
    aerodyn_files = [path.join(path.dirname(batch.runs[i]['input_file']), 'NRELOffshrBsline5MW_AeroDyn.ipt') for i in range(2)]
    with open(aerodyn_files[0]) as fp:
        aerodyn1 = fp.read()
    with open(aerodyn_files[1]) as fp:
        aerodyn2 = fp.read()
    assert 'TurbSim_5_12' in aerodyn1
    assert 'TurbSim_6_14' in aerodyn2
