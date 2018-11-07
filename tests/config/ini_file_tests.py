import pytest

from os import path

from multiwindcalc.config.ini_file import IniFileConfiguration

INI_CONTENTS = """[multiwindcalc]
workers=4
outdir=c:/some_directory
plugins=nrel:some.path.to.Class,other:another.path.to.Class

[server]
port=8082
"""

@pytest.fixture
def config(tmpdir):
    ini_file = path.join(tmpdir, 'config.ini')
    with open(ini_file, 'w') as fp:
        fp.write(INI_CONTENTS)
    return IniFileConfiguration(ini_file)

def test_config_reads_string_correctly(config):
    assert config.get('multiwindcalc', 'outdir') == 'c:/some_directory'

def test_config_reads_int_correctly(config):
    assert config.get('multiwindcalc', 'workers', type=int) == 4

def test_config_reads_int_from_other_category_correctly(config):
    assert config.get('server', 'port', type=int) == 8082

def test_config_returns_none_if_value_not_found(config):
    assert config.get('server', 'hostname') is None

def test_config_returns_default_if_default_provided(config):
    assert config.get('server', 'hostname', default='localhost') == 'localhost'

def test_config_returns_list_value(config):
    assert config.get('multiwindcalc', 'plugins', type=list) == ['nrel:some.path.to.Class', 'other:another.path.to.Class']