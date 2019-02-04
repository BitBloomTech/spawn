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
"""Functions to set up logging
"""
import logging
from logging import handlers
from enum import Enum
from os import path, makedirs

import appdirs

class CustomLogLevel(Enum):
    """Enum to add custom log level TRACE
    """
    TRACE = 5

TRACE = CustomLogLevel.TRACE.value

LOG_DIR = path.join(appdirs.user_log_dir(), 'spawn')

def configure_logging(log_level, command_name, log_console=True, log_file=True):
    """Configure logging

    :param log_level: The log level (error, warning, info, debug, trace)
    :type log_level: str
    :param command_name: The name of the invoked subcommand
    :type command_name: str
    :param log_console: ``True`` if logs should be displayed in the console; otherwise ``False``.
        Defaults to ``True``.
    :type log_console: bool
    :param log_file: ``True`` if logs should be written to file; otherwise ``False``.
        Defaults to ``True``.
    :type log_file: bool
    """
    logging.addLevelName(TRACE, 'TRACE')

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        enum_level = getattr(CustomLogLevel, log_level.upper(), None)
        if isinstance(enum_level, CustomLogLevel):
            numeric_level = enum_level.value
        else:
            numeric_level = logging.INFO

    logging.getLogger().setLevel(numeric_level)

    rollover_bytes = 1024 * 1024
    dir_name = LOG_DIR
    if not path.isdir(dir_name):
        makedirs(dir_name)

    if log_file:
        file_handler = handlers.RotatingFileHandler(
            path.join(LOG_DIR, command_name + '.log'),
            mode='w',
            maxBytes=rollover_bytes,
            backupCount=10
        )
        file_handler.doRollover()
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)

    if log_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logging.getLogger().addHandler(console_handler)
