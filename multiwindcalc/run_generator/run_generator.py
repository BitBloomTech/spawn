import os.path as path
import numpy as np
from multiwindcalc.input_editors.nrel_input_editor import TurbSimInputEditor, FastInputEditor
from .combinators import gridify
from .directory_handler import DirectoryHandler


def _get_field(spec, field):
    try:
        return spec[field]
    except KeyError:
        raise KeyError('\'{}\' not found in load case specification'.format(field))


def _make_turbsim_editor(spec):
    return TurbSimInputEditor(_get_field(spec, 'base_wind_input'))


def _combine_variables(load_case):
    try:
        type = load_case['type']
        if type == 'grid':
            return gridify(load_case['variables'])
        else:
            raise ValueError('{} not recognised as load case type'.format(type))
    except KeyError as key:
        raise KeyError('{} not found in load case description'.format(key))


def _jsonise_type(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    else:
        return obj


def _get_run_defs(load_case):
    if load_case['type'] == 'grid':
        return gridify(load_case['variables'])
    elif load_case['type'] == 'list':
        return load_case['variables']
    else:
        raise TypeError('load case type \'{}\' not recognised'.format(load_case['type']))


def __absolutise_path_field(spec, key, root):
    if not path.isabs(spec[key]):
        spec[key] = path.join(root, spec[key])


def generate_preprocessing_runs(spec, base_folder, batch, spec_paths_root=None):

    if spec_paths_root:
        __absolutise_path_field(spec, 'base_wind_input', spec_paths_root)
        __absolutise_path_field(spec, 'wind_executable', spec_paths_root)

    wind_file_editor = _make_turbsim_editor(spec)
    wind_executable = _get_field(spec, 'wind_executable')

    for load_case in spec['load_cases']:
        run_defs = _get_run_defs(load_case)
        directory = DirectoryHandler(base_folder, path.join('wind', load_case['path']))
        for run in run_defs:
            directory.make_new_dir()
            input_file_path = path.join(directory.abspath, 'TurbSim.inp')
            output_file_path = path.join(directory.abspath, 'TurbSim.wnd')

            wind_file_editor.write(path.join(directory.abspath, input_file_path), run)
            batch.add_run(str(directory.relative_path), wind_executable, input_file_path)
            run['wind_file'] = path.splitext(output_file_path)[0]   # without extension - note this is FAST specific
            for k in run.keys():
                run[k] = _jsonise_type(run[k])
        load_case['variables'] = run_defs
        load_case['type'] = 'list'


def generate_time_domain_runs(spec, base_folder, batch, spec_paths_root=None):

    if spec_paths_root:
        __absolutise_path_field(spec, 'base_time_domain_input', spec_paths_root)
        __absolutise_path_field(spec, 'time_domain_executable', spec_paths_root)

    base_input_file = _get_field(spec, 'base_time_domain_input')
    fast_editor = FastInputEditor(base_input_file)
    executable = _get_field(spec, 'time_domain_executable')

    for load_case in spec['load_cases']:
        run_defs = _get_run_defs(load_case)
        directory = DirectoryHandler(base_folder, path.join('runs', load_case['path']))
        for run in run_defs:
            directory.make_new_dir()
            input_file_path = path.join(directory.abspath, path.basename(base_input_file))
            fast_editor.write(path.join(directory.abspath, input_file_path), run)
            batch.add_run(str(directory.relative_path), executable, input_file_path)
            run['output'] = path.splitext(input_file_path)[0] + fast_editor.output_extension
