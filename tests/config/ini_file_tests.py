# spawn
# Copyright (C) 2018, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
import pytest

from os import path

from spawn.config.ini_file import IniFileConfiguration

INI_CONTENTS = """[spawn]
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
    assert config.get('spawn', 'outdir') == 'c:/some_directory'

def test_config_reads_int_correctly(config):
    assert config.get('spawn', 'workers', parameter_type=int) == 4

def test_config_reads_int_from_other_category_correctly(config):
    assert config.get('server', 'port', parameter_type=int) == 8082

def test_config_returns_none_if_value_not_found(config):
    assert config.get('server', 'hostname') is None

def test_config_returns_default_if_default_provided(config):
    assert config.get('server', 'hostname', default='localhost') == 'localhost'

def test_config_returns_list_value(config):
    assert config.get('spawn', 'plugins', parameter_type=list) == ['nrel:some.path.to.Class', 'other:another.path.to.Class']