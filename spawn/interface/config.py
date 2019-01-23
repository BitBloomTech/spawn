# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
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
"""Interface method for creating a spawn config object
"""
from spawn.config import (
    CommandLineConfiguration, CompositeConfiguration,
    DefaultConfiguration, IniFileConfiguration
)

def spawn_config(**kwargs):
    """Create a spawn config object with extra kwargs
    """
    command_line_config = CommandLineConfiguration(**kwargs)
    ini_file_config = IniFileConfiguration(
        command_line_config.get(CommandLineConfiguration.default_category, 'config_file')
    )
    default_config = DefaultConfiguration()
    return CompositeConfiguration(command_line_config, ini_file_config, default_config)
