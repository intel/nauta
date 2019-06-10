#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List

STREAM_HANDLER = logging.StreamHandler(stream=sys.stdout)


def initialize_logger(package_name) -> logging.Logger:
    STREAM_HANDLER.setLevel(logging.CRITICAL)
    logger = logging.getLogger(package_name)
    logging.basicConfig(level=logging.DEBUG, handlers=[STREAM_HANDLER])

    return logger


def get_verbosity_level():
    return STREAM_HANDLER.level


def set_global_logging_level(log_level):
    for key in logging.Logger.manager.loggerDict:
        for handler in logging.getLogger(key).handlers:
            if not isinstance(handler, TimedRotatingFileHandler):
                handler.setLevel(log_level)


# ALWAYS called on CLI command init
def set_verbosity_level(verbosity):
    if verbosity == 0:
        logging_level = logging.CRITICAL
    elif verbosity == 1:
        logging_level = logging.INFO
    else:
        logging_level = logging.DEBUG

    set_global_logging_level(logging_level)
    STREAM_HANDLER.setLevel(logging_level)


def setup_log_file(log_file_directory: str, log_level=logging.DEBUG, log_backup_count=30):
    root_logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s  - %(message)s')
    file_handler = TimedRotatingFileHandler(filename=f'{log_file_directory}/nctl_logs',
                                            when='d', interval=1, backupCount=log_backup_count)
    file_handler.rotator = nauta_log_rotator
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)

    return file_handler


def nauta_log_rotator(source, dest):
    if os.path.exists(source):
        try:
            os.rename(source, dest)
        except PermissionError:
            pass  # When NAUTA doesn't have permissions to log file, just skip this log rotation iteration.


def configure_logger_for_external_packages(pack_name: str, initial_log_level: int,
                                           handlers: List[logging.Handler] = None):
    loggers_keys_list = [key for key in logging.Logger.manager.loggerDict if key.startswith(pack_name)]  # type: ignore
    for key in loggers_keys_list:
        logger = logging.getLogger(key)
        logger.propagate = False
        if handlers:
            for handler in handlers:
                logger.addHandler(handler)
        # default system logger's handler - should be present in all loggers
        STREAM_HANDLER.setLevel(initial_log_level)
        logger.addHandler(STREAM_HANDLER)
