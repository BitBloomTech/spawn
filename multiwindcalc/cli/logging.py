import logging
from logging import handlers
from enum import Enum
from os import path, makedirs

import appdirs

class CustomLogLevel(Enum):
    TRACE = 5

TRACE = CustomLogLevel.TRACE.value

LOG_DIR = appdirs.user_log_dir()

def configure_logging(log_level, console):
    logging.addLevelName(TRACE, 'TRACE')

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        enum_level = getattr(CustomLogLevel, log_level.upper(), None)
        if isinstance(enum_level, CustomLogLevel):
            numeric_level = enum_level.value
        else:
            numeric_level = logging.INFO

    logging.getLogger().setLevel(numeric_level)

    rollover_bytes = 5 * 1024
    dir_name = LOG_DIR
    if not path.isdir(dir_name):
        makedirs(dir_name)

    file_handler = handlers.RotatingFileHandler(
        path.join(LOG_DIR, 'application.log'),
        mode='w',
        maxBytes=rollover_bytes,
        backupCount=10
    )
    file_handler.doRollover()
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logging.getLogger().addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(console_handler)
