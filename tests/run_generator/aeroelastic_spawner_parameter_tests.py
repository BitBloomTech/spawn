from os import path
import pytest
import tempfile
import pandas as pd
import numpy as np
import luigi
from wetb.fast import fast_io
from multiwindcalc.simulation_inputs.nrel_simulation_input import FastInput, TurbsimInput
from multiwindcalc.run_generator.fast_simulation_spawner import FastSimulationSpawner, TurbsimSpawner
import example_data


def run_and_get_results(spawner):
    task = spawner.spawn()
    luigi.build([task], local_scheduler=True, log_level='WARNING')
    data, info = fast_io.load_output(task.output().path)
    return pd.DataFrame(data, columns=info['attribute_names'])


@pytest.fixture()
def spawner(tmpdir):
    turbsim_input = TurbsimInput.from_file(example_data.turbsim_input_file)
    wind_spawner = TurbsimSpawner(path.join(tmpdir, 'wind'), turbsim_input, example_data.turbsim_exe)
    fast_input = FastInput.from_file(example_data.fast_input_file)
    spawner = FastSimulationSpawner(path.join(tmpdir, 'runs'), fast_input, example_data.fast_exe, wind_spawner)
    spawner.wind_speed = 8.0
    spawner.output_start_time = 0.0
    spawner.simulation_time = 1.0
    return spawner


@pytest.fixture(scope='module')
def baseline():
    with tempfile.TemporaryDirectory() as tmpdir:
        s = spawner(tmpdir)
        return run_and_get_results(s)


@pytest.mark.parametrize('property,type', [
    ('output_start_time', float),
    ('simulation_time', float),
    ('wind_speed', float),
    ('turbulence_intensity', float),
    ('turbulence_seed', int)
])
def test_property_type(spawner, property, type):
    assert isinstance(getattr(spawner, property), type)


def test_output_start_time(baseline, spawner):
    spawner.output_start_time = 0.5
    res = run_and_get_results(spawner)
    assert res.shape[0] == 6


def test_simulation_time(baseline, spawner):
    spawner.simulation_time = 2 * spawner.simulation_time
    res = run_and_get_results(spawner)
    assert res.shape[0] == 2 * baseline.shape[0]


def test_wind_speed(baseline, spawner):
    spawner.wind_speed = 2 * spawner.wind_speed
    res = run_and_get_results(spawner)
    assert pytest.approx(2*np.mean(baseline['WindVxi']), np.mean(res['WindVxi']))


def test_turbulence_intensity(baseline, spawner):
    assert spawner.turbulence_intensity < 1.0
    spawner.turbulence_intensity = 2 * spawner.turbulence_intensity
    res = run_and_get_results(spawner)
    assert pytest.approx(2*np.std(baseline['WindVxi']), np.std(res['WindVxi']))


def test_turbulence_seed(baseline, spawner):
    spawner.turbulence_seed += 1
    res = run_and_get_results(spawner)
    assert np.all(baseline['WindVxi'] != res['WindVxi'])
