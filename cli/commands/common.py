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
import shutil
import time
import random
from enum import Enum
from typing import Tuple

from util.config import EXPERIMENTS_DIR_NAME, Config, Fields
from util.logger import initialize_logger
from util.exceptions import KubectlIntError

# definitions of headers content for different commands
EXPERIMENT_NAME = "Experiment"
EXPERIMENT_STATUS = "Status"
EXPERIMENT_MESSAGE = "Message"
EXPERIMENT_PARAMETERS = "Parameters used"

log = initialize_logger('commands.common')


def create_environment(experiment_name: str, file_location: str, folder_location: str) -> str:
    """
    Creates a complete environment for executing a training using draft.

    :param experiment_name: name of an experiment used to create a folder
                            with content of an experiment
    :param file_location: location of a training script
    :param folder_location: location of a folder with additional data
    :return: (experiment_folder)
    experiment_folder - folder with experiment's artifacts
    In case of any problems during creation of an enviornment it throws an
    exception with a description of a problem
    """
    log.debug("Create environment - start")
    message_prefix = "Experiment's environment hasn't been created. Reason - {}"

    # create a folder for experiment's purposes
    experiment_path = os.path.join(Config.get(Fields.CONFIG_PATH), EXPERIMENTS_DIR_NAME, experiment_name)

    # copy folder content
    if folder_location:
        try:
            shutil.copytree(folder_location, experiment_path)
        except Exception as exe:
            log.exception("Create environment - copying training folder error.")
            raise KubectlIntError(message_prefix.format("Additional folder cannot"
                                                        " be copied into experiment's folder."))

    try:
        if not os.path.exists(experiment_path):
            os.makedirs(experiment_path)
    except Exception as exe:
        log.exception("Create environment - creating experiment folder error.")
        raise KubectlIntError(message_prefix.format("Folder with experiments' data cannot be created."))

    # copy training script - it overwrites the file taken from a folder_location
    try:
        shutil.copy2(file_location, experiment_path)
    except Exception as exe:
        log.exception("Create environment - copying training script error.")
        raise KubectlIntError(message_prefix.format("Training script cannot be created."))

    log.debug("Create environment - end")
    return experiment_path


def generate_experiment_name(suffix: str="") -> str:
    time_part = time.strftime("%Y%m%d%H%M%S")
    random_part = random.randrange(0, 999)
    experiment_name = "t" + time_part + str(random_part).zfill(3) + suffix

    return experiment_name


def delete_environment(experiment_folder: str):
    """
    Deletes draft environment located in a folder given as a paramater
    :param experiment_folder: location of an environment
    """
    try:
        shutil.rmtree(experiment_folder)
    except Exception as exe:
        log.error("Delete environment - i/o error : {}".format(exe))


def convert_to_number(s: str) -> int or float:
    """
    Converts string to number of a proper type.

    :param s: - string to be converted
    :return: number in a proper format - float or int
    """
    try:
        return int(s)
    except ValueError:
        return float(s)


class ExperimentStatus(Enum):
    SUBMITTED = "Submitted"
    ERROR = "Error"


class ExperimentDescription:
    def __init__(self, name: str="", status: ExperimentStatus=None,
                 error_message: str="", folder: str="", parameters: Tuple[str, ...]=None):
        self.name = name
        self.status = status
        self.error_message = error_message
        self.folder = folder
        self.parameters = parameters

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name \
                   and self.status == other.status \
                   and self.error_message == other.error_message \
                   and self.folder == other.folder \
                   and self.parameters == other.parameters

        return False

    def formatted_parameters(self):
        # parameters are stored in a tuple of strings
        if self.parameters:
            return "\n".join(self.parameters)
        else:
            return ""

    def formatted_status(self):
        return self.status.name
