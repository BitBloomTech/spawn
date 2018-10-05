import os
from os import path
import copy
from multiwindcalc.simulation_inputs.nrel_simulation_input import AerodynInput
from multiwindcalc.tasks.simulation import FastSimulationTask
from multiwindcalc.spawners.aeroelastic_simulation import AeroelasticSimulationSpawner
from multiwindcalc.spawners.directory_handler import DirectoryHandler


def quote(strpath):
    if strpath[0] != '"' or strpath[-1] != '"':
        return '"' + strpath + '"'


class FastSimulationSpawner(AeroelasticSimulationSpawner):
    """Spawns FAST simulation tasks with wind generation dependency if necessary"""

    def __init__(self, directory, fast_input, fast_exe, wind_spawner, working_dir=None):
        self._directory = directory if isinstance(directory, DirectoryHandler) else DirectoryHandler(directory)
        self._input = fast_input
        self._executable = fast_exe
        self._wind_spawner = wind_spawner
        self._working_dir = working_dir if working_dir is not None else os.getcwd()
        # non-arguments:
        self._aerodyn_input = AerodynInput.from_file(self._input['ADFile'])
        self._wind_environment_changed = False
        self._wind_task = None

    def spawn(self, additional_folder=False):
        directory = self._directory.branch() if additional_folder else self._directory
        preproc_tasks = self._spawn_preproc_tasks(directory, additional_folder)
        sim_input_file = path.join(directory.abspath, 'simulation.ipt')
        self._input.to_file(sim_input_file)
        sim_task = FastSimulationTask('run ' + directory.relative_path,
                                      self._executable,
                                      sim_input_file,
                                      preproc_tasks,
                                      _working_dir=self._working_dir)
        return sim_task

    def _spawn_preproc_tasks(self, run_directory, additional_folder):
        preproc_tasks = []
        # Generate new wind file if needed
        if self._wind_environment_changed:
            self._wind_task = self._wind_spawner.spawn(additional_folder=additional_folder)
            self._aerodyn_input['WindFile'] = quote(self._wind_task.wind_file_path)
            aerodyn_file_path = path.join(run_directory.abspath, 'aerodyn.ipt')
            self._aerodyn_input.to_file(aerodyn_file_path)
            self._input['ADFile'] = quote(aerodyn_file_path)
            self._wind_environment_changed = False
        return [self._wind_task] if self._wind_task is not None else []

    def branch(self, branch_id=None):
        branched_spawner = copy.copy(self)
        branched_spawner._directory = self._directory.branch(branch_id)
        branched_spawner._input = copy.deepcopy(self._input)
        branched_spawner._wind_spawner = self._wind_spawner.branch(branch_id)
        return branched_spawner

    # Simulation options
    def get_output_start_time(self):
        return float(self._input['TStart'])

    def set_output_start_time(self, time):
        self._input['TStart'] = time

    def get_simulation_time(self):
        """Total simulation time in seconds"""
        return float(self._input['TMax'])

    def set_simulation_time(self, time):
        self._input['TMax'] = time
        self._wind_spawner.simulation_time = time

    def get_operation_mode(self):
        raise NotImplementedError('Incapable of determining operation mode') # this is a tricky one!

    def set_operation_mode(self, mode):
        """
        Operation mode:
        'normal' - power production run with generator on and rotor free
        'idling' - generator off but rotor free
        'parked' - generator off and rotor fixed
        The operation mode is set here according to recommendation in FASTv7 user manual page 33 and 34
        """
        if mode not in ['normal', 'idling', 'parked']:
            raise ValueError('mode \'' + mode + '\' unrecognised')

        # Generator
        large_time = self._make_large_time()
        if mode == 'normal':
            self._input['GenTiStr'] = True
            self._input['TimGenOn'] = 0.0  # time to turn generator on
            self._input['TimGenOf'] = large_time  # never turn generator off
            self._free_pitch()
        else:
            self._input['GenTiStr'] = True
            self._input['TimGenOn'] = large_time  # never turn generator on
            self._input['TimGenOf'] = 0.0  # time to turn generator off
            self._fix_pitch()

        # rotor freedom
        if mode == 'normal' or mode == 'idling':
            self._input['GenDOF'] = True
        else:
            self._input['GenDOF'] = False
        if mode == 'idling' or mode == 'parked':
            self.initial_rotor_speed = 0.0

    # Initial Conditions
    def get_initial_rotor_speed(self):
        """Rotor speed at start of simulation in rpm"""
        return float(self._input['RotSpeed'])

    def set_initial_rotor_speed(self, rotor_speed):
        self._input['RotSpeed'] = rotor_speed

    def get_initial_azimuth(self):
        """Rotor azimuth of blade 1 at start of simulation in degrees"""
        return float(self._input['Azimuth'])

    def set_initial_azimuth(self, azimuth):
        self._input['Azimuth'] = azimuth

    def get_initial_yaw_angle(self):
        """Nacelle yaw angle at start of simulation in degrees; clockwise from North"""
        return float(self._input['NacYaw'])  # 'YawNeut' could be another possibility here

    def set_initial_yaw_angle(self, angle):
        self._input['NacYaw'] = angle

    def get_initial_pitch_angle(self):
        raise NotImplementedError()

    def set_initial_pitch_angle(self, angle):
        """Sets pitch angle for all blades at start of simulation; in degrees, positive towards feather"""
        for i in range(self.number_of_blades):
            bld = '({})'.format(i+1)
            self._input['BlPitch' + bld] = angle
            # if the pitch manoeuvre ends at time zero, the final pitch is actually the initial pitch too!
            if float(self._input['TPitManE' + bld]) <= 0.0:
                self._input['BlPitchF' + bld] = angle

    # Properties deferred to wind generation spawner:
    def get_wind_speed(self):
        """Mean wind speed in m/s"""
        return self._wind_spawner.wind_speed

    def set_wind_speed(self, speed):
        self._wind_spawner.wind_speed = speed
        self._wind_environment_changed = True

    def get_turbulence_intensity(self):
        """Turbulence intensity as a fraction (not %): ratio of wind speed standard deviation to mean wind speed"""
        return self._wind_spawner.turbulence_intensity

    def set_turbulence_intensity(self, turbulence_intensity):
        self._wind_spawner.turbulence_intensity = turbulence_intensity
        self._wind_environment_changed = True

    def get_turbulence_seed(self):
        """Random number seed for turbulence generation"""
        return self._wind_spawner.turbulence_seed

    def set_turbulence_seed(self, seed):
        self._wind_spawner.turbulence_seed = seed
        self._wind_environment_changed = True

    def get_wind_shear(self):
        """Vertical wind shear exponent"""
        return self._wind_spawner.wind_shear

    def set_wind_shear(self, exponent):
        self._wind_spawner.wind_shear = exponent
        self._wind_environment_changed = True

    def get_upflow(self):
        """Wind inclination in degrees from the horizontal"""
        return self._wind_spawner.upflow

    def set_upflow(self, angle):
        self._wind_spawner.upflow = angle
        self._wind_environment_changed = True

    # Properties of turbine, for which setting is not supported
    def get_number_of_blades(self):
        return int(self._input['NumBl'])

    # non-properties
    def _fix_pitch(self, pitch_angle=None):
        if pitch_angle is not None:
            self.initial_pitch_angle = pitch_angle
        for i in range(self.number_of_blades):
            bld = '({})'.format(i+1)
            self._input['BlPitchF' + bld] = self._input['BlPitch' + bld]
            self._input['TPitManS' + bld] = 0.0
            self._input['TPitManE' + bld] = 0.0

    def _free_pitch(self):
        large_time = self._make_large_time()
        for i in range(self.number_of_blades):
            bld = '({})'.format(i+1)
            self._input['TPitManS' + bld] = large_time
            self._input['TPitManE' + bld] = large_time

    def _make_large_time(self):
        return max(9999.9, float(self._input['TMax']) + 1.0)

