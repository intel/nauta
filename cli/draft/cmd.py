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

import logging
import os
from typing import List
import re

from util.config import Config
from util.system import execute_system_command
from util.logger import initialize_logger, get_verbosity_level
from cli_text_consts import DraftCmdTexts as Texts


logger = initialize_logger('draft.cmd')

DRAFT_BIN = 'draft'
DRAFT_HOME_FOLDER = ".draft"
DRAFT_LOGS_FOLDER = "logs"

DOCKER_IP_ADDRESS = "127.0.0.1"


def call_draft(args: List[str], cwd: str = None, namespace: str = None, logs_size: int = 0) \
        -> (str, int, str):
    config_path = Config().config_path
    full_command = [os.path.join(config_path, DRAFT_BIN)]
    full_command.extend(args)
    if get_verbosity_level() == logging.DEBUG:
        full_command.append('--debug')

    env = os.environ.copy()
    env['DRAFT_HOME'] = os.path.join(config_path, DRAFT_HOME_FOLDER)
    if namespace:
        env['TILLER_NAMESPACE'] = namespace
    return execute_system_command(full_command, env=env, cwd=cwd, logs_size=logs_size)


def create(working_directory: str = None, pack_type: str = None) -> (str, int, str):
    command = ['create']
    if pack_type:
        command.append('--pack={}'.format(pack_type))
    output, exit_code, log_output = call_draft(args=command, cwd=working_directory)

    if not exit_code:
        output, exit_code = check_create_status(output)
    else:
        output = translate_create_status_description(output)

    return output, exit_code, log_output


def up(working_directory: str = None, namespace: str = None) -> (str, int, str):
    output, exit_code, log_output = call_draft(args=['up'], cwd=working_directory, namespace=namespace, logs_size=200)
    # displaying logs from draft - only in debug mode
    pattern = "Inspect the logs with `draft logs (.*)`"

    p = re.compile(pattern)

    search_result = p.search(output)

    try:
        if search_result:
            draft_logs_filename = search_result.group(1)

            config_path = Config().config_path
            filename = os.path.join(config_path, DRAFT_HOME_FOLDER, DRAFT_LOGS_FOLDER, draft_logs_filename)

            with open(filename, "r") as file:
                logger.debug("Draft logs:")
                logger.debug(file.read())
                logger.debug(20*"-")
        else:
            logger.debug("Lack of logs from draft.")
    except Exception as exe:
        # exception here shouldn't block finishing of the operation
        error_message = Texts.PROBLEMS_DURING_GETTING_DRAFT_LOGS.format(exception=str(exe))
        logger.error(error_message)

    if not exit_code:
        output, exit_code = check_up_status(output)

    return output, exit_code, log_output


def check_up_status(output: str) -> (str, int):
    """
    Checks whether up command was finished with success.
    :param output: output of the 'up' command
    :return: (message, exit_code):
    - exit_code - 0 if operation was a success
    - message - message with a description of a problem
    """
    if "Building Docker Image: SUCCESS" not in output:
        return Texts.DOCKER_IMAGE_NOT_BUILT, 100
    elif "Pushing Docker Image: SUCCESS" not in output:
        return Texts.DOCKER_IMAGE_NOT_SENT, 101
    elif "Releasing Application: SUCCESS" not in output:
        return Texts.APP_NOT_RELEASED, 102
    return "", 0


def check_create_status(output: str) -> (str, int):
    """
    Checks whether create command was finished with success.
    :param output: output of the 'create' command
    :return: (message, exit_code):
    - exit_code - 0 if operation was a success
    - message - message with a description of a problem
    """
    if "--> Ready to sail" not in output:
        return Texts.DEPLOYMENT_NOT_CREATED, 100
    return "", 0


def translate_create_status_description(output: str) -> str:
    """
    Converts a description of a known error to human readable
    form

    :param output: - message to be converted
    :return: converted message - if the message given as input param
    is recognized by the system, if is not recognized - original
    output
    """
    if "Error: could not load pack:" in output:
        return Texts.PACK_NOT_EXISTS
    else:
        return output
