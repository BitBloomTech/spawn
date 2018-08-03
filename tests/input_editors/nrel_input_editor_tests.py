from os import path
import tempfile
from multiwindcalc.input_editors.nrel_input_editor import TurbSimInputEditor, AeroDynInputEditor, FastInputEditor
from ..component_tests import example_data_folder

__examples_folder = path.join(example_data_folder, 'fast_input_files')


def test_turbsim_input_editor_edits_file():
    editor = TurbSimInputEditor(path.join(__examples_folder, 'TurbSim.inp'))
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.ipt')
    temp.close()
    editor.write(temp.name, {'wind_speed': 10.0, 'turbulence_intensity': 12.0, 'turbulence_model': '"IECKAI"'})

    with open(temp.name, 'r') as fp:
        lines = fp.readlines()
    wind_speed_line = lines[36].split()
    assert(wind_speed_line[0] == str(10.0))
    assert(wind_speed_line[1] == 'URef')
    turbulence_line = lines[31].split()
    assert(turbulence_line[0] == str(12.0))
    assert(turbulence_line[1] == 'IECturbc')
    turb_model_line = lines[29].split()
    assert(turb_model_line[0] == '"IECKAI"')
    assert(turb_model_line[1] == 'TurbModel')


def test_turbsim_input_editor_writes_multiple_input_files_without_persisting_fields():
    original_file = path.join(__examples_folder, 'TurbSim.inp')
    with open(original_file, 'r') as fp:
        wind_speed = fp.readlines()[36].split()[0]
    editor = TurbSimInputEditor(original_file)
    temp_file1 = tempfile.NamedTemporaryFile()
    temp_file2 = tempfile.NamedTemporaryFile()
    temp_file1.close()
    temp_file2.close()
    editor.write(temp_file1.name, {'wind_speed': 10.0})
    editor.write(temp_file2.name, {'turbulence_intensity': 12.0})
    with open(temp_file2.name, 'r') as fp:
        lines = fp.readlines()
    new_wind_speed = lines[36].split()[0]
    assert(new_wind_speed == wind_speed)


def test_aerodyn_editor_edits_file():
    editor = AeroDynInputEditor(path.join(__examples_folder, 'NRELOffshrBsline5MW_AeroDyn.ipt'))
    new_wind_file = r'"WindData\TurbSim"'
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.ipt')
    temp.close()
    editor.write(temp.name, {'wind_file': new_wind_file})
    with open(temp.name, 'r') as fp:
        lines = fp.readlines()
    found = False
    for line in lines:
        parts = line.split()
        if parts[1] == 'WindFile':
            assert(parts[0] == new_wind_file)
            found = True
            break
    assert found


def test_aerodyn_paths_are_absolutised():
    editor = AeroDynInputEditor(path.join(__examples_folder, 'NRELOffshrBsline5MW_AeroDyn.ipt'))
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.ipt')
    temp.close()
    editor.write(temp.name, {})
    with open(temp.name, 'r') as fp:
        lines = fp.readlines()
    for i in range(19, 26):
        path.isfile(lines[25].strip('"'))


def test_fast_paths_are_absolutised():
    editor = FastInputEditor(path.join(__examples_folder, 'NRELOffshrBsline5MW_Onshore.fst'))
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.ipt')
    temp.close()
    editor.write(temp.name, {})
    with open(temp.name, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            parts = line.split()
            if len(parts) > 1 and 'BldFile' in parts[1]:
                assert(path.isfile(parts[0].strip('"')))


def test_fast_editor_edits_fast_input_file():
    editor = FastInputEditor(path.join(__examples_folder, 'NRELOffshrBsline5MW_Onshore.fst'))
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.ipt')
    temp.close()
    editor.write(temp.name, {'total_run_time': 620.0, 'output_start_time': 20.0})
    with open(temp.name, 'r') as fp:
        lines = fp.readlines()
    assert(lines[9].split()[0] == str(620.0))
    assert(lines[172].split()[0] == str(20.0))
