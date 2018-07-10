#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

import sys
import logging
from logging.handlers import TimedRotatingFileHandler


STREAM_HANDLER = logging.StreamHandler(stream=sys.stdout)


def initialize_logger(package_name) -> logging.Logger:
    STREAM_HANDLER.setLevel(logging.CRITICAL)
    logger = logging.getLogger(package_name)
    logging.basicConfig(level=logging.DEBUG, handlers=[STREAM_HANDLER])
    return logger


def get_verbosity_level():
    return STREAM_HANDLER.level


# ALWAYS called on CLI command init
def set_verbosity_level(verbosity):
    logging_level = logging.CRITICAL

    if verbosity == 1:
        logging_level = logging.INFO
    elif verbosity >= 2:
        logging_level = logging.DEBUG

    STREAM_HANDLER.setLevel(logging_level)


def setup_log_file(log_file_directory: str, log_level=logging.DEBUG, log_backup_count=30):
    root_logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s  - %(message)s')
    file_handler = TimedRotatingFileHandler(filename=f'{log_file_directory}/dlsctl_logs',
                                            when='d', interval=1, backupCount=log_backup_count)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)
