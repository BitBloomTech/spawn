from abc import abstractmethod, abstractproperty
import os.path as path
from multiwindcalc.input_editors.input_editor import InputEditor


def _absolutise_path(line, root_dir, local_path):
    local_path = local_path.strip('"')
    return line.replace(local_path, str(path.join(root_dir, local_path)))


class NRELInputEditor(InputEditor):
    def __init__(self, base_file_path):
        with open(base_file_path, 'r') as fp:
            self._input_lines = fp.readlines()

    def write(self, file_path, editions):
        field_editions = self._get_field_names(editions)
        with open(file_path, 'w') as fw:
            for line in self._input_lines:
                parts = line.split()
                if len(parts) > 1 and parts[1] in field_editions:
                    line = line.replace(parts[0], str(field_editions[parts[1]]))
                fw.write(line)

    @property
    @abstractmethod
    def output_extension(self):
        pass

    def _get_field_names(self, edits, error_if_not_found=False):
        field_name_edits = {}
        field_name_map = self._get_field_name_map()
        for var_name, value in edits.items():
            try:
                field_name = field_name_map[var_name]
                field_name_edits[field_name] = value
            except KeyError:
                if error_if_not_found:
                    raise KeyError('Variable \'{}\' unrecognised for {} input file'.format(var_name, self._get_name()))
        return field_name_edits

    def _get_index_and_parts(self, field):
        for i, line in enumerate(self._input_lines):
            parts = line.split()
            if len(parts) > 1 and parts[1] == field:
                return i, parts
        raise KeyError('field \'{}\' not found in {}'.format(field, str(self._base_file_path)))

    def _get_field(self, field):
        return self._get_index_and_parts(field)[1][0]

    def get_variable(self, variable):
        try:
            field_name = self._get_field_name_map()[variable]
        except KeyError:
            raise KeyError('Variable \'{}\' unrecognised for {} input file'.format(variable, self._get_name()))
        return self._get_field(field_name)

    @abstractmethod
    def _get_field_name_map(self):
        pass

    @abstractmethod
    def _get_name(self):
        pass


class TurbSimInputEditor(NRELInputEditor):
    def __init__(self, base_file_path):
        super().__init__(base_file_path)
        self._field_name_map = {
            'wind_speed': 'URef',
            'turbulence_intensity': 'IECturbc',
            'turbulence_seed': 'RandSeed1',
            'turbulence_model': 'TurbModel'
        }

    @property
    def output_extension(self):
        return '.wnd'

    def _get_field_name_map(self):
        return self._field_name_map

    def _get_name(self):
        return 'TurbSim'


class AeroDynInputEditor(NRELInputEditor):
    def __init__(self, base_file_path):
        super().__init__(base_file_path)
        self._field_name_map = {
            'wind_file': 'WindFile',
            'air_density': 'AirDens'
        }
        root_dir = path.dirname(path.realpath(base_file_path))
        self._absolutise_paths(root_dir)

    @property
    def output_extension(self):
        return ''

    def _get_field_name_map(self):
        return self._field_name_map

    def _get_name(self):
        return 'AeroDyn'

    def _absolutise_paths(self, root_dir):
        num_foils = int(self._get_field('NumFoil'))
        index, parts = self._get_index_and_parts('FoilNm')
        for i in range(index, index+num_foils):
            self._input_lines[i] = _absolutise_path(self._input_lines[i], root_dir, self._input_lines[i].split()[0])

    @property
    def field_name_map(self):
        return self._field_name_map


class FastInputEditor(NRELInputEditor):
    def __init__(self, base_file_path):
        self._base_file_path = base_file_path
        with open(base_file_path, 'r') as fp:
            self._input_lines = fp.readlines()
        self._field_name_map = {
            'total_run_time': 'TMax',
            'output_start_time': 'TStart',
            'integration_time_step': 'DT'
        }

        base_dir = path.dirname(path.realpath(base_file_path))
        self._aerodyn_file = self._get_field('ADFile').strip('"')
        self._aerodyn_editor = AeroDynInputEditor(path.join(base_dir, self._aerodyn_file))

        self._absolutise_paths(base_dir)

    def write(self, file_path, editions):
        self._write_aerodyn_input(path.dirname(path.realpath(file_path)), editions)
        super().write(file_path, editions)

    @staticmethod
    def changes_wind_environment(editions):
        return 'wind_speed' in editions or 'turbulence_intensity' in editions or 'turbulence_seed' in editions \
               or 'turbulence_model' in editions

    @property
    def output_extension(self):
        return '.outb'

    def get_variable(self, variable):
        try:
            field_name = self._get_field_name_map()[variable]
            return self._get_field(field_name)
        except KeyError:
            try:
                value = self._aerodyn_editor.get_variable(variable)
                return value
            except KeyError:
                raise KeyError('Variable \'{}\' unrecognised for {} input file'.format(variable, self._get_name()))

    def _write_aerodyn_input(self, directory, fast_editions):
        aerodyn_abspath = path.join(directory, self._aerodyn_file)
        aerodyn_editions = {}
        used_keys = []
        for key, value in fast_editions.items():
            if key in self._aerodyn_editor.field_name_map:
                aerodyn_editions[key] = value
                used_keys.append(key)
        for key in used_keys:
            del fast_editions[key]
        self._aerodyn_editor.write(aerodyn_abspath, aerodyn_editions)

    def _get_field_name_map(self):
        return self._field_name_map

    def _get_name(self):
        return 'FAST'

    @property
    def field_name_map(self):
        return self._field_name_map

    def _absolutise_paths(self, base_dir):
        for i in range(len(self._input_lines)):
            parts = self._input_lines[i].split()
            if len(parts) > 1 and (parts[1] == 'TwrFile' or 'BldFile' in parts[1] or parts[1] == 'ADAMSFile'):
                self._input_lines[i] = _absolutise_path(self._input_lines[i], base_dir, parts[0])
