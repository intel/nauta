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
import sys
from typing import List

from util.system import execute_system_command
from util.logger import initialize_logger

log = initialize_logger('draft.cmd')

draft_path = os.path.dirname(sys.executable)

DRAFT_BIN = 'draft'

DOCKER_IP_ADDRESS = "127.0.0.1"


def call_draft(args: List[str]) -> (str, int):
    full_command = [DRAFT_BIN]
    full_command.extend(args)

    envs = os.environ.copy()
    envs['DRAFT_HOME'] = os.path.join(draft_path, ".draft")
    envs['PATH'] = os.getenv('PATH') + ':' + draft_path

    return execute_system_command(full_command, env=envs)


def create():
    output, exit_code = call_draft(['create', '--pack=tf-training'])
    print(output)


def up():
    output, exit_code = call_draft(['up'])
    print(output)
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
    docker_location = DOCKER_IP_ADDRESS + ":" + registry_port

    CONFIGURE_DRAFT_PORT_COMMAND = ["config", "set", "registry", docker_location]

    return call_draft(CONFIGURE_DRAFT_PORT_COMMAND)
