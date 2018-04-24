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

import os
from util.logger import initialize_logger
import platform

log = initialize_logger('util.config')
# environmental variable with a dlsctl home folder
ENV_DLSCTL_HOME = 'DLSCTL_HOME'
LINUX_ENV_HOME = 'HOME'
WINDOWS_ENV_HOME = 'USERPROFILE'

# name of a config folder
CONFIG_FOLDER = '.dlsctl'

# name of a folder with experiment's data
EXPERIMENTS_FOLDER = 'tmp'


def create_home_folder() -> str:
    """
    Creates a home folder of a cli application - if it doesn't exist.

    :return:
    - name of a home folder, if empty - home folder doesn't exist and hasn't
      been created
    """
    home_folder = ""
    log.debug("Create home folder - start")
    try:
        try:
            home_folder = os.environ[ENV_DLSCTL_HOME]
        except KeyError:
            if platform.system() == 'Windows':
                home_folder = os.environ[WINDOWS_ENV_HOME]
            else:
                home_folder = os.environ[LINUX_ENV_HOME]

        home_folder = os.path.join(home_folder, CONFIG_FOLDER)

        if not os.path.exists(home_folder):
            os.makedirs(home_folder)
    except Exception as exe:
        log.error("Create home folder - error : {}".format(exe))
        home_folder = ""

    log.debug("Create home folder - end")
    return home_folder
