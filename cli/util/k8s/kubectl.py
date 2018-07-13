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
import time
import random

from typing import Optional

import platform_resources.users as users_api
from util import system
from util.logger import initialize_logger
from util.exceptions import KubectlIntError, KubectlConnectionError, LocalPortOccupiedError
from util.k8s.k8s_info import get_app_services, find_namespace
from util.app_names import DLS4EAppNames
from util.system import check_port_availability

logger = initialize_logger('util.kubectl')

MAX_NUMBER_OF_TRIES = 1000
START_PORT = 3000
END_PORT = 65535


def start_port_forwarding(k8s_app_name: DLS4EAppNames, port: int = None, app_name: str = None,
                          number_of_retries: int = 0, namespace: str = None) -> (subprocess.Popen, Optional[int], int):
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
    :param port: if given - the system will try to use it as a local port
    :return:
        instance of a process with proxy, tunneled port and container port
    """
    logger.debug("Start port forwarding")

    try:
        service_node_port = None
        service_container_port = None

        app_services = get_app_services(dls4e_app_name=k8s_app_name, namespace=namespace, app_name=app_name)

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

        if port:
            if not check_port_availability(port):
                error_msg = f"Port {port} is occupied. Please try to use another one."
                logger.error(error_msg)
                raise LocalPortOccupiedError(error_msg)
            tunnel_port = port
        else:
            for port in random.sample(range(START_PORT, END_PORT), k=MAX_NUMBER_OF_TRIES):
                if check_port_availability(port):
                    tunnel_port = port
                    break
            else:
                error_msg = "Available port cannot be found."
                logger.error(error_msg)
                raise LocalPortOccupiedError(error_msg)

        port_forward_command = ['kubectl', 'port-forward', f'--namespace={namespace}', f'service/{service_name}',
                                f'{tunnel_port}:{service_container_port}']

        logger.debug(port_forward_command)

        process = None
        if number_of_retries:
            for i in range(number_of_retries-1):
                try:
                    process = system.execute_subprocess_command(port_forward_command)
                except Exception:
                    logger.exception("Error during setting up proxy - retrying.")
                else:
                    break
                time.sleep(5)

        if not process:
            process = system.execute_subprocess_command(port_forward_command)

    except KubectlIntError as exe:
        raise RuntimeError(exe)
    except LocalPortOccupiedError as exe:
        raise exe
    except Exception:
        raise RuntimeError("Other error during creation of port proxy.")

    logger.info("Port forwarding - proxy set up")
    return process, tunnel_port, service_container_port


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
        error_message = "Error during checking user's presence."
        logger.error(error_message)
        raise KubectlIntError(error_message) from exe


def delete_k8s_object(kind: str, name: str):
    delete_command = ['kubectl', 'delete', kind, name]
    logger.debug(delete_command)
    output, err_code = system.execute_system_command(delete_command)
    logger.debug(f"delete_k8s_object - output : {err_code} - {output}")
    if err_code:
        raise RuntimeError(f"Error when deleting k8s object: {output}")


def check_connection_to_cluster():
    check_connection_cmd = ['kubectl', 'get', 'pods']
    logger.debug(check_connection_cmd)
    output, err_code = system.execute_system_command(check_connection_cmd)
    logger.debug(f"check_connection_to_cluster - output : {err_code} - {output}")
    if err_code:
        raise KubectlConnectionError(f"Cannot connect to K8S cluster: {output}")
