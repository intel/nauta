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

import subprocess

from typing import Optional

import platform_resources.users as users_api
from util import system
from util.logger import initialize_logger
from util.exceptions import KubectlIntError
from draft.cmd import set_registry_port
from util.k8s.k8s_info import get_app_services, find_namespace
from util.app_names import DLS4EAppNames

logger = initialize_logger('util.kubectl')


def start_port_forwarding(k8s_app_name: DLS4EAppNames) -> (subprocess.Popen, Optional[int], int):
    """
    Creates a proxy responsible for forwarding requests to and from a
    kubernetes' local docker proxy. In case of any errors during creating the
    process - throws a RuntimeError exception with a short description of
    a cause of a problem.
    When proxy created by this function is no longer needed - it should
    be closed by calling kill() function on a process returned by this
    function.

    :param k8s_app_name: name of kubernetes application for tunnel creation
                         value taken from DLS4EAppNames enum

    :return:
        instance of a process with proxy, tunneled port and container port
    """
    logger.debug("Start port forwarding")

    try:
        service_node_port = None
        namespace = None
        app_services = get_app_services(k8s_app_name.value)
        if app_services:
            service_node_port = app_services[0].spec.ports[0].node_port
            if service_node_port:
                logger.debug('Service node port pod has been found: {}'.
                             format(service_node_port))

            service_container_port = app_services[0].spec.ports[0].port
            if service_container_port:
                logger.debug('Service container port has been found: {}'.
                             format(service_container_port))
            service_name = app_services[0].metadata.name
            namespace = app_services[0].metadata.namespace

        if not service_node_port and not service_container_port:
            logger.error(f'Cannot find open ports for {k8s_app_name} app')
            raise KubectlIntError("Missing port during creation of port proxy.")

        if k8s_app_name == DLS4EAppNames.DOCKER_REGISTRY:
            # setting draft conf, only for docker-registry case
            dc_output, dc_exit_code = set_registry_port(service_node_port)
            if dc_exit_code:
                logger.error("Port forwarding - exception - setting draft config failed : {}".format(
                    dc_output
                ))
                raise KubectlIntError("Setting draft config failed.")

        if not service_node_port:
            ports_to_be_forwarded = str(service_container_port)
        else:
            ports_to_be_forwarded = f'{service_node_port}:{service_container_port}'

        port_forward_command = ['kubectl', 'port-forward', f'--namespace={namespace}', f'service/{service_name}',
                                ports_to_be_forwarded]
        logger.debug(port_forward_command)

        process = system.execute_subprocess_command(port_forward_command)

    except KubectlIntError as exe:
        raise RuntimeError(exe)
    except Exception:
        raise RuntimeError("Other error during creation of port proxy.")

    logger.info("Port forwarding - proxy set up")
    return process, service_node_port, service_container_port


def check_users_presence(username: str) -> bool:
    """
    Checks whether a user with a given name exists. It searches also for a namespace
    with a name equal to the given username

    :param username: username
    :return: True if a user exists, False otherwise
    In case of problems during gathering user's data - it raises an exception.
    """
    if find_namespace(username):
        logger.debug("Namespace {} already exists.".format(username))
        return True

    try:
        user_data = users_api.get_user_data(username)

        return user_data and user_data.name == username
    except Exception as exe:
        print(exe)
        error_message = "Error during checking user's presence."
        logger.error(error_message)
        raise KubectlIntError(error_message) from exe

    return False
