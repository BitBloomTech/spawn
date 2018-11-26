"""Implementation of :class:`AeroelasticSimulationSpawner` for FAST
"""
import os
from os import path
import copy

from multiwindcalc.plugins.wind import AeroelasticSimulationSpawner
from multiwindcalc.util import quote

from .simulation_input import AerodynInput
from .tasks import FastSimulationTask

class FastSimulationSpawner(AeroelasticSimulationSpawner):
    """Spawns FAST simulation tasks with wind generation dependency if necessary"""

    def __init__(self, fast_input, wind_spawner):
        """Initialises :class:`FastSimulationSpawner`

        :param fast_input: The FAST input
        :type fast_input: :class:`FastInput`
        :parm wind_spawner: The TurbSim/wind calculation spawner
        :type wind_spawner: :class:`TurbsimSpawner`
        """
        self._input = fast_input
        self._wind_spawner = wind_spawner
        # non-arguments:
        self._aerodyn_input = AerodynInput.from_file(self._input['ADFile'])
        self._wind_environment_changed = False
        self._wind_task = None
        # intermediate parameters
        self._pitch_manoeuvre_rate = None
        self._yaw_manoeuvre_rate = None

    def spawn(self, path_, metadata):
        """Spawn a simulation task

        :param path_: The output path for the task
        :type path_: str
        :param metadata: Metadata to add to the task
        :type metadata: dict

        :returns: The simulation task
        :rtype: :class:`SimulationTask`
        """
        if not path.isabs(path_):
            raise ValueError('Must provide an absolute path')
        if not path.isdir(path_):
            os.makedirs(path_)
        wind_input_files = self._spawn_preproc_tasks(path_, metadata)
        sim_input_file = path.join(path_, 'simulation.ipt')
        self._input.to_file(sim_input_file)
        sim_task = FastSimulationTask('run ' + path_, sim_input_file, _dependencies=wind_input_files, _metadata=metadata)
        return sim_task

    def _spawn_preproc_tasks(self, path_, metadata):
        # Generate new wind file if needed
        if self._wind_environment_changed:
            self._wind_task = self._wind_spawner.spawn(path_, metadata)
            self._aerodyn_input['WindFile'] = quote(self._wind_task.wind_file_path)
            aerodyn_file_path = path.join(path_, 'aerodyn.ipt')
            self._aerodyn_input.to_file(aerodyn_file_path)
            self._input['ADFile'] = quote(aerodyn_file_path)
            self._wind_environment_changed = False
        return [self._wind_task] if self._wind_task is not None else []

    def branch(self):
        """Create a copy of this spawner

        :returns: A copy of this spawner with all values equal
        :rtype: :class:`FastSimulationSpawner`
        """
        branched_spawner = copy.copy(self)
        branched_spawner._input = copy.deepcopy(self._input)
        branched_spawner._wind_spawner = self._wind_spawner.branch()
        return branched_spawner

    # Simulation options
    def get_output_start_time(self):
        return float(self._input['TStart'])

    def set_output_start_time(self, time):
        dt = time - self.get_output_start_time()
        self._input['TStart'] = time
        self._input['TMax'] = float(self._input['TMax']) + dt  # Adjust max time so that simulation time is constant
        self._wind_spawner.duration = float(self._input['TMax'])

    def get_simulation_time(self):
        return float(self._input['TMax']) - self.get_output_start_time()

    def set_simulation_time(self, time):
        total_time = float(time) + self.get_output_start_time()
        self._input['TMax'] = float(time) + self.get_output_start_time()
        self._wind_spawner.analysis_time = time
        self._wind_spawner.duration = total_time

    # Initial Conditions
    def get_initial_rotor_speed(self):
        return float(self._input['RotSpeed'])

    def set_initial_rotor_speed(self, rotor_speed):
        self._input['RotSpeed'] = rotor_speed

    def get_initial_azimuth(self):
        return float(self._input['Azimuth'])

    def set_initial_azimuth(self, azimuth):
        self._input['Azimuth'] = azimuth

    def get_initial_yaw(self):
        return float(self._input['NacYaw'])  # 'YawNeut' could be another possibility here

    def set_initial_yaw(self, angle):
        self._input['NacYaw'] = angle

    def get_initial_pitch(self):
        raise NotImplementedError()

    def set_initial_pitch(self, angle):
        for i in range(self.number_of_blades):
            bld = self._blade_string(i+1)
            self._input['BlPitch' + bld] = angle
            # if the pitch manoeuvre ends at time zero, the final pitch is actually the initial pitch too!
            if float(self._input['TPitManE' + bld]) <= 0.0:
                self._input['BlPitchF' + bld] = angle

    # Supervisory operation
    def get_operation_mode(self):
        raise NotImplementedError('Incapable of determining operation mode')  # this is a tricky one!

    def set_operation_mode(self, mode):
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

    def get_transient_mode(self):
        raise NotImplementedError('Incapable of determining transient mode')  # Indeterminable!

    def set_transient_mode(self, mode):
        if mode not in ['stationary', 'startup', 'shutdown']:
            raise ValueError("mode '" + mode + "' unrecognised")

        large_time = self._make_large_time()
        if mode == 'stationary':
            self._input['PCMode'] = 1
            self._input['TimGenOn'] = 0.0
            self._input['TimGenOff'] = large_time
        elif mode == 'startup':
            self._input['PCMode'] = 0
            self._input['GenTiStr'] = False
        elif mode == 'shutdown':
            self._input['TiGenOn'] = 0.0

    def get_pitch_manoeuvre_time(self):
        raise NotImplementedError('Incapable of determining pitch manoeuvre time for all blades at once')

    def set_pitch_manoeuvre_time(self, time):
        for i in range(self.number_of_blades):
            self.set_blade_pitch_manoeuvre_time(i+1, time)

    def get_blade_pitch_manoeuvre_time(self, index):
        return self._input['TPitManS' + self._blade_string(index)]

    def set_blade_pitch_manoeuvre_time(self, index, time):
        self._input['PCMode'] = 0
        self._input['TPitManS' + self._blade_string(index)] = time
        self._reconcile_pitch_manoeuvre(index)

    def get_pitch_manoeuvre_rate(self):
        return self._pitch_manoeuvre_rate

    def set_pitch_manoeuvre_rate(self, pitch_rate):
        self._pitch_manoeuvre_rate = float(pitch_rate)
        for i in range(self.number_of_blades):
            self._reconcile_pitch_manoeuvre(i+1)

    def get_final_pitch(self):
        raise NotImplementedError('Incapable of determining final pitch angle for all blades at once')

    def set_final_pitch(self, angle):
        for i in range(self.number_of_blades):
            self.set_blade_final_pitch(i+1, angle)

    def get_blade_final_pitch(self, index):
        return float(self._input['BlPitchF' + self._blade_string(index)])

    def set_blade_final_pitch(self, index, angle):
        self._input['BlPitchF' + self._blade_string(index)] = angle
        self._reconcile_pitch_manoeuvre(index)

    def _reconcile_pitch_manoeuvre(self, blade_number):
        if self._pitch_manoeuvre_rate is not None:
            bld = self._blade_string(blade_number)
            self._input['TPitManE' + bld] = float(self._input['TPitManS' + bld]) + \
                (float(self._input['BlPitchF' + bld]) - float(self._input['BlPitch' + bld]))\
                / self._pitch_manoeuvre_rate

    def get_yaw_manoeuvre_time(self):
        return float(self._input['TYawManS'])

    def set_yaw_manoeuvre_time(self, time):
        self._input['TYawManS'] = time
        self._input['YCMode'] = 0
        self._reconcile_yaw_manoeuvre()

    def get_yaw_manoeuvre_rate(self):
        return self._yaw_manoeuvre_rate

    def set_yaw_manoeuvre_rate(self, rate):
        self._yaw_manoeuvre_rate = float(rate)
        self._reconcile_yaw_manoeuvre()

    def get_final_yaw(self):
        return float(self._input['NacYawF'])

    def set_final_yaw(self, angle):
        self._input['NacYawF'] = angle
        self._reconcile_yaw_manoeuvre()

    def _reconcile_yaw_manoeuvre(self):
        if self._yaw_manoeuvre_rate is not None:
            self._input['TYawManE'] = self.get_yaw_manoeuvre_time() + \
                (self.get_final_yaw() - self.get_initial_yaw()) / self._yaw_manoeuvre_rate

    # Turbine faults
    def get_grid_loss_time(self):
        return float(self._input['TimGenOf'])

    def set_grid_loss_time(self, time):
        self._input['GenTiStp'] = True
        self._input['TimGenOf'] = time

    # Properties deferred to wind generation spawner:
    def get_wind_speed(self):
        return self._wind_spawner.wind_speed

    def set_wind_speed(self, speed):
        self._wind_spawner.wind_speed = speed
        self._wind_environment_changed = True

    def get_turbulence_intensity(self):
        return self._wind_spawner.turbulence_intensity

    def set_turbulence_intensity(self, turbulence_intensity):
        self._wind_spawner.turbulence_intensity = turbulence_intensity
        self._wind_environment_changed = True

    def get_turbulence_seed(self):
        return self._wind_spawner.turbulence_seed

    def set_turbulence_seed(self, seed):
        self._wind_spawner.turbulence_seed = seed
        self._wind_environment_changed = True

    def get_wind_shear(self):
        return self._wind_spawner.wind_shear

    def set_wind_shear(self, exponent):
        self._wind_spawner.wind_shear = exponent
        self._wind_environment_changed = True

    def get_upflow(self):
        return self._wind_spawner.upflow

    def set_upflow(self, angle):
        self._wind_spawner.upflow = angle
        self._wind_environment_changed = True

    def get_wind_file(self):
        return self._aerodyn_input['WindFile']

    def set_wind_file(self, file):
        self._aerodyn_input['WindFile'] = quote(file)
        self._wind_environment_changed = False  # presumes file is externally generated

    # Properties of turbine, for which setting is not supported
    def get_number_of_blades(self):
        return int(self._input['NumBl'])

    # non-properties
    @staticmethod
    def _blade_string(blade_number):
        return '({})'.format(blade_number)

    def _fix_pitch(self, pitch_angle=None):
        if pitch_angle is not None:
            self.initial_pitch = pitch_angle
        for i in range(self.number_of_blades):
            bld = self._blade_string(i+1)
            self._input['BlPitchF' + bld] = self._input['BlPitch' + bld]
            self._input['TPitManS' + bld] = 0.0
            self._input['TPitManE' + bld] = 0.0

    def _free_pitch(self):
        large_time = self._make_large_time()
        for i in range(self.number_of_blades):
            bld = self._blade_string(i+1)
            self._input['TPitManS' + bld] = large_time
            self._input['TPitManE' + bld] = large_time

    def _set_for_all_blades(self, key, value):
        for i in range(self.number_of_blades):
            bld = self._blade_string(i+1)
            self._input[key + bld] = value

    def _make_large_time(self):
        return max(9999.9, float(self._input['TMax']) + 1.0)

