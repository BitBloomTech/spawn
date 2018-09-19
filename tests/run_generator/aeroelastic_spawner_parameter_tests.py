from os import path
import pytest
import tempfile
import pandas as pd
import numpy as np
import math
import luigi
from wetb.fast import fast_io
from multiwindcalc.simulation_inputs.nrel_simulation_input import FastInput, TurbsimInput
from multiwindcalc.run_generator.fast_simulation_spawner import FastSimulationSpawner, TurbsimSpawner
import example_data


def run_and_get_results(spawner):
    task = spawner.spawn(additional_folder=True)
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
    ('turbulence_seed', int),
    ('wind_shear', float),
    ('upflow', float),
    ('initial_rotor_speed', float),
    ('initial_azimuth', float),
    ('initial_yaw_angle', float),
    ('number_of_blades', int)
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


@pytest.mark.parametrize('key,value,output_name', [
    ('initial_rotor_speed', 7.0, 'RotSpeed'),
    ('initial_azimuth', 180.0, 'Azimuth'),
    ('initial_yaw_angle', 90.0, 'YawPzn'),
    ('initial_pitch_angle', 30.0, 'BldPitch1')
])
def test_initial_values(spawner, key, value, output_name):
    setattr(spawner, key, value)
    res = run_and_get_results(spawner)
    assert res[output_name][0] == pytest.approx(value, rel=0.1)


def test_operating_mode(spawner):
    spawner.operation_mode = 'idling'
    spawner.initial_pitch_angle = 30.0
    res = run_and_get_results(spawner)
    assert np.all(res['BldPitch1'] == 30.0)
    assert np.all(res['GenPwr'] <= 0.0)
    assert np.all(res['RotSpeed'] != 0.0)
    assert np.all(abs(res['RotSpeed']) < 1.0)
    spawner.operation_mode = 'parked'
    spawner.initial_pitch_angle = 90.0
    res2 = run_and_get_results(spawner)
    assert np.all(res2['BldPitch1'] == 90.0)
    assert np.all(res2['GenPwr'] <= 0.0)
    assert np.all(abs(res2['RotSpeed']) <= 0.01)    # rotor speed is slightly non-zero due to drive-train flexibility
    spawner.operation_mode = 'normal'
    spawner.initial_pitch_angle = 0.0
    res3 = run_and_get_results(spawner)
    assert np.all(res3['BldPitch1'] <= 10.0)
    assert np.all(res3['GenPwr'] >= 0.0)
    assert np.all(res3['RotSpeed'] > 0.0)


def test_turbulence_seed(baseline, spawner):
    spawner.turbulence_seed += 1
    res = run_and_get_results(spawner)
    assert np.all(baseline['WindVxi'] != res['WindVxi'])


def test_wind_speed(baseline, spawner):
    spawner.wind_speed = 2 * spawner.wind_speed
    res = run_and_get_results(spawner)
    assert np.mean(res['WindVxi']) == pytest.approx(2*np.mean(baseline['WindVxi']), rel=0.1)


def test_turbulence_intensity(baseline, spawner):
    assert spawner.turbulence_intensity < 1.0
    spawner.turbulence_intensity = 2 * spawner.turbulence_intensity
    res = run_and_get_results(spawner)
    assert np.std(res['WindVxi']) == pytest.approx(2*np.std(baseline['WindVxi']), rel=1e-3)


def test_turbulence_seed(baseline, spawner):
    spawner.turbulence_seed += 1
    res = run_and_get_results(spawner)
    assert np.all(baseline['WindVxi'] != res['WindVxi'])


def test_wind_shear(baseline, spawner):
    spawner.wind_shear = 0.3
    res = run_and_get_results(spawner)
    assert np.all(res['YawBrMyp'] > baseline['YawBrMyp'])  # increase in shear gives predominantly 0P increase in tower-top overturning moment


def test_upflow(baseline, spawner):
    spawner.upflow = 10.0
    res = run_and_get_results(spawner)
    assert np.mean(res['WindVxi']) < np.mean(baseline['WindVxi'])
    upflow_baseline = np.mean(np.arctan2(baseline['WindVzi'], baseline['WindVxi']))
    upflow_new = np.mean(np.arctan2(res['WindVzi'], res['WindVxi']))
    assert math.degrees(upflow_new - upflow_baseline) == pytest.approx(spawner.upflow, abs=0.1)
