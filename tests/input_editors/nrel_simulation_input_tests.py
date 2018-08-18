from os import path
import pytest
import tempfile
from multiwindcalc.simulation_inputs.nrel_simulation_input import TurbsimInput, AerodynInput, FastInput
from ..component_tests import example_data_folder

__examples_folder = path.join(example_data_folder, 'fast_input_files')


@pytest.mark.parametrize('cls,file,key', [
    (TurbsimInput, 'TurbSim.inp', 'CTStartTime'),
    (AerodynInput, 'NRELOffshrBsline5MW_AeroDyn.ipt', 'BldNodes'),
    (FastInput, 'NRELOffshrBsline5MW_Onshore.fst', 'NBlGages')
])
def test_read_write_round_trip(cls, file, key):
    _input = cls.from_file(path.join(__examples_folder, file))
    with tempfile.TemporaryDirectory() as outfile:
        name = path.join(outfile, 'temp.txt')
        _input.to_file(name)
        _input2 = cls.from_file(name)
    assert _input[key] == _input2[key]


@pytest.mark.parametrize('cls,file,key,value', [
    (TurbsimInput, 'TurbSim.inp', 'URef', 11.0),
    (AerodynInput, 'NRELOffshrBsline5MW_AeroDyn.ipt', 'WindFile', 'Other.wnd'),
    (FastInput, 'NRELOffshrBsline5MW_Onshore.fst', 'TMax', 300.0)
])
def test_writes_edited_fields(cls, file, key, value):
    _input = cls.from_file(path.join(__examples_folder, file))
    _input[key] = value
    with tempfile.TemporaryDirectory() as outfile:
        name = path.join(outfile, 'temp.txt')
        _input.to_file(name)
        _input2 = cls.from_file(name)
    assert _input2[key] == str(value)


@pytest.mark.parametrize('cls,file,keys', [
    (AerodynInput, 'NRELOffshrBsline5MW_AeroDyn.ipt', ['FoilNm']),
    (FastInput, 'NRELOffshrBsline5MW_Onshore.fst', ['BldFile(1)', 'BldFile(3)', 'TwrFile'])
])
def test_paths_are_absolute(cls, file, keys):
    _input = cls.from_file(path.join(__examples_folder, file))
    for k in keys:
        f = _input[k]
        assert path.isfile(f)
