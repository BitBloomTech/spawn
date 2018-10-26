import pytest

from multiwindcalc.runners.factories import RunnerFactory
from multiwindcalc.runners.process_runner import ProcessRunner

@pytest.fixture
def factory():
    return RunnerFactory()

def test_factory_create_process_returns_process_runner(factory):
    assert isinstance(factory.create('process', '42', 'my_input_file', 'exe_path'), ProcessRunner)

def test_factory_create_raises_error_for_non_process(factory):
    with pytest.raises(ValueError):
        assert factory.create('aws', '42', 'my_input_file')
        
def test_factory_create_raises_error_if_not_all_process_args_supplied(factory):
    with pytest.raises(TypeError):
        assert factory.create('process', '42', 'my_input_file')