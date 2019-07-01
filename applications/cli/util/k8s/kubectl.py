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

import subprocess
import time
import random
from enum import Enum

from typing import Tuple

from util import system
from util.logger import initialize_logger
from util.exceptions import KubernetesError, KubectlConnectionError, LocalPortOccupiedError
from util.k8s.k8s_info import get_app_services
from util.app_names import NAUTAAppNames
from util.system import check_port_availability
from cli_text_consts import UtilKubectlTexts as Texts

logger = initialize_logger('util.kubectl')

MAX_NUMBER_OF_TRIES = 1000
START_PORT = 3000
END_PORT = 65535


class UserState(Enum):
    ACTIVE = "Active"
    TERMINATING = "Terminating"
    NOT_EXISTS = "Not_Exists"


def find_random_available_port() -> int:
    for port in random.sample(range(START_PORT, END_PORT), k=MAX_NUMBER_OF_TRIES):
        if check_port_availability(port):
            tunnel_port = port
            break
    else:
        error_msg = Texts.NO_AVAILABLE_PORT_ERROR_MSG
        logger.error(error_msg)
        raise LocalPortOccupiedError(error_msg)

    return tunnel_port


def start_port_forwarding(k8s_app_name: NAUTAAppNames, port: int = None, app_name: str = None,
                          number_of_retries: int = 0,
                          namespace: str = None) -> Tuple[subprocess.Popen, int, int]:
    """
    Creates a proxy responsible for forwarding requests to and from a
    kubernetes' local docker proxy. In case of any errors during creating the
    process - throws a RuntimeError exception with a short description of
    a cause of a problem.
    When proxy created by this function is no longer needed - it should
    be closed by calling kill() function on a process returned by this
    function.

    :param k8s_app_name: name of kubernetes application for tunnel creation
                         value taken from NAUTAAppNames enum
    :param port: if given - the system will try to use it as a local port. Random port will be used
     if that port is not available
    :return:
        instance of a process with proxy, tunneled port and container port
    """
    logger.debug("Start port forwarding")

    try:
        service_node_port = None
        service_container_port = None

        app_services = get_app_services(nauta_app_name=k8s_app_name, namespace=namespace, app_name=app_name)

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
            raise KubernetesError(Texts.PROXY_CREATION_MISSING_PORT_ERROR_MSG)

        if port and check_port_availability(port):
            tunnel_port = port
        else:
            tunnel_port = find_random_available_port()

        port_forward_command = ['kubectl', 'port-forward', f'--namespace={namespace}',
                                f'service/{service_name}', f'{tunnel_port}:{service_container_port}', '-v=4']

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

    except KubernetesError as exe:
        raise RuntimeError(exe)
    except LocalPortOccupiedError as exe:
        raise exe
    except Exception:
        raise RuntimeError(Texts.PROXY_CREATION_OTHER_ERROR_MSG)

    logger.info("Port forwarding - proxy set up")
    return process, tunnel_port, service_container_port


def delete_k8s_object(kind: str, name: str):
    delete_command = ['kubectl', 'delete', kind, name]
    logger.debug(delete_command)
    output, err_code, log_output = system.execute_system_command(delete_command)
    logger.debug(f"delete_k8s_object - output : {err_code} - {log_output}")
    if err_code:
        raise RuntimeError(Texts.K8S_OBJECT_DELETE_ERROR_MSG.format(output=log_output))


def check_connection_to_cluster():
    check_connection_cmd = ['kubectl', 'get', 'pods']
    logger.debug(check_connection_cmd)
    output, err_code, log_output = system.execute_system_command(check_connection_cmd)
    logger.debug(f"check_connection_to_cluster - output : {err_code} - {log_output}")
    if err_code:
        raise KubectlConnectionError(Texts.K8S_CLUSTER_NO_CONNECTION_ERROR_MSG.format(output=log_output))


def get_top_for_pod(name: str, namespace: str) -> Tuple[str, str]:
    """
    Returns cpu and memory usage for a pod with a given name located in a given namespace
    :param name: name of a pod
    :param namespace:  namespace where the pod resided. Optional - if not given, function searches the pod in
                        current namespace
    :return: tuple containing two values - cpu and memory usage expressed in k8s format
    """
    top_command = ["kubectl", "top", "pod", name]

    if namespace:
        top_command.extend(["-n", namespace])
    output, err_code, log_output = system.execute_system_command(top_command)
    if err_code:
        raise KubectlConnectionError(Texts.K8S_CLUSTER_NO_CONNECTION_ERROR_MSG.format(output=log_output))

    if output:
        lines = output.split("\n")

        if lines and len(lines) > 1:
            second_line = lines[1]
            if second_line:
                split_second_line = second_line.split()
                if split_second_line and len(split_second_line) > 2:
                    return (split_second_line[1], split_second_line[2])

    logger.error(Texts.TOP_COMMAND_ERROR_LOG.format(output=log_output))
    raise KubernetesError(Texts.TOP_COMMAND_ERROR)
