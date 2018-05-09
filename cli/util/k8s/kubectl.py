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
import subprocess

from util.logger import initialize_logger
from util.exceptions import KubectlIntError
from draft.cmd import set_registry_port
from util.k8s.k8s_info import get_app_pods, get_app_services, get_pod_status, PodStatus

logger = initialize_logger('util.kubectl')


def start_port_forwarding(k8s_app_name: str) -> (subprocess.Popen, int, int):
    """
    Creates a proxy responsible for forwarding requests to and from a
    kubernetes' local docker proxy. In case of any errors during creating the
    process - throws a RuntimeError exception with a short description of
    a cause of a problem.
    When proxy created by this function is no longer needed - it should
    be closed by calling kill() function on a process returned by this
    function.

    :param k8s_app_name: name of kubernetes application for tunnel creation

    :return:
        instance of a process with proxy, tunneled port and container port
    """
    logger.debug("Start port forwarding")

    try:
        running_pod_name = None
        service_node_port = None
        namespace = None

        app_pods = get_app_pods(k8s_app_name)
        for pod in app_pods:
            pod_name = pod.metadata.name
            pod_namespace = pod.metadata.namespace
            pod_status = get_pod_status(pod_name, pod_namespace)

            if pod_status == PodStatus.RUNNING:
                running_pod_name = pod_name
                namespace = pod_namespace
                logger.debug('Running pod for {} has been found: {}'.format(k8s_app_name, running_pod_name))
                break

        if not running_pod_name:
            logger.error('Cannot find running k8s pod for {}'.format(k8s_app_name))
            raise KubectlIntError("Missing running pod name during creation of port proxy.")

        app_services = get_app_services(k8s_app_name)
        if app_services:
            service_node_port = app_services[0].spec.ports[0].node_port
            if service_node_port:
                logger.debug('Service node port for {} pod has been found: {}'.format(running_pod_name, service_node_port))

            service_container_port = app_services[0].spec.ports[0].port
            if service_container_port:
                logger.debug('Service container port for {} pod has been found: {}'.format(running_pod_name, service_container_port))

        if not service_node_port or not service_container_port:
            logger.error(f'Cannot find open port for {k8s_app_name} app pod')
            raise KubectlIntError("Missing pod port during creation of port proxy.")

        if k8s_app_name == 'docker-registry':
            # setting draft conf, only for docker-registry case
            dc_output, dc_exit_code = set_registry_port(service_node_port)
            if dc_exit_code:
                logger.error("Port forwarding - exception - setting draft config failed : {}".format(
                    dc_output
                ))
                raise KubectlIntError("Setting draft config failed.")

        port_forward_command = ['kubectl', 'port-forward', f'--namespace={namespace}', running_pod_name,
                                f'{service_node_port}:{service_container_port}']

        # if a log level is set to DEBUG - additional information from creatoin of a proxy are sent to console
        std_output_destination = None if logger.getEffectiveLevel() == logging.DEBUG else subprocess.DEVNULL
        std_error_destination = subprocess.STDOUT if logger.getEffectiveLevel() == logging.DEBUG else subprocess.DEVNULL

        process = subprocess.Popen(args=port_forward_command, stdout=std_output_destination,
                                   stderr=std_error_destination)

        if not process:
            logger.error("Port forwarding - exception - process doesn't exist.")
            raise KubectlIntError("Port proxy hasn't been created.")

    except KubectlIntError as exe:
        raise RuntimeError(exe)
    except Exception:
        logger.exception("Port forwarding - exception - other.")
        raise RuntimeError("Other error during creation of port proxy.")

    logger.info("Port forwarding - proxy set up")
    return process, service_node_port, service_container_port
