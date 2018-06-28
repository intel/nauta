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

from util.config import Config
from util.system import execute_system_command
from util.logger import initialize_logger

log = initialize_logger('draft.cmd')

DRAFT_BIN = 'draft'
DRAFT_HOME_FOLDER = ".draft"

DOCKER_IP_ADDRESS = "127.0.0.1"


def call_draft(args: List[str], cwd: str = None, namespace: str = None) -> (str, int):
    config_path = Config().config_path
    full_command = [os.path.join(config_path, DRAFT_BIN)]
    full_command.extend(args)
    if log.getEffectiveLevel() == logging.DEBUG:
        full_command.append('--debug')

    env = os.environ.copy()
    env['DRAFT_HOME'] = os.path.join(config_path, DRAFT_HOME_FOLDER)
    if namespace:
        env['TILLER_NAMESPACE'] = namespace
    return execute_system_command(full_command, env=env, cwd=cwd)


def create(working_directory: str = None, pack_type: str = None) -> (str, int):
    command = ['create']
    if pack_type:
        command.append('--pack={}'.format(pack_type))
    output, exit_code = call_draft(args=command, cwd=working_directory)

    if not exit_code:
        output, exit_code = check_create_status(output)
    else:
        output = translate_create_status_description(output)

    return output, exit_code


def up(working_directory: str = None, namespace: str = None) -> (str, int):
    output, exit_code = call_draft(args=['up'], cwd=working_directory, namespace=namespace)
    if not exit_code:
        output, exit_code = check_up_status(output)

    return output, exit_code


def set_registry_port(registry_port: str) -> (str, int):
    """
    Sets port of docker's registry used by draft instance.

    :param registry_port: port under which local k8s registry is available
    :return: (output, exit_code)
    - output - message from execution of a command returned by the system
    - exit_code - 0 - operation was a success, otherwise some error occurred during
                its execution
    """
    docker_location = f'{DOCKER_IP_ADDRESS}:{registry_port}'

    configure_draft_port_command = ["config", "set", "registry", docker_location]

    return call_draft(configure_draft_port_command)


def check_up_status(output: str) -> (str, int):
    """
    Checks whether up command was finished with success.
    :param output: output of the 'up' command
    :return: (message, exit_code):
    - exit_code - 0 if operation was a success
    - message - message with a description of a problem
    """
    if "Building Docker Image: SUCCESS" not in output:
        return "Docker image hasn't been built.", 100
    elif "Pushing Docker Image: SUCCESS" not in output:
        return "Docker image hasn't been sent to the cluster.", 101
    elif "Releasing Application: SUCCESS" not in output:
        return "Application hasn't been released.", 102
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
        return "Deployment hasn't been created.", 100
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
        return "Chosen pack doesn't exist."
    else:
        return output
