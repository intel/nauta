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

from util.logger import initialize_logger, is_debug_level
from util.system import execute_system_command
from util.exceptions import KubectlIntError
from draft.cmd import set_registry_port

logger = initialize_logger('util.kubectl')

# namespace where a local registry has been deployed
NAMESPACE = "kube-system"

# labels used to find a local-registry deployment
LABELS = ["-l", "app=docker-registry"]

GETTING_POD_NAME_COMMAND = ["kubectl", "get", "--namespace={}".format(NAMESPACE), "--no-headers=true", "pods", "-o",
                            "custom-columns=:metadata.name"]
GETTING_POD_NAME_COMMAND.extend(LABELS)

GETTING_PORT_COMMAND = ["kubectl", "get", "--namespace={}".format(NAMESPACE), "--no-headers=true", "svc", "-o",
                        "go-template={{range .items}}{{range.spec.ports}}{{.nodePort}}{{end}}{{end}}"]
GETTING_PORT_COMMAND.extend(LABELS)

# port exposed by a kubernetes' local docker registry
DOCKER_PORT = "5000"


def start_port_forwarding():
    """
    Creates a proxy responsible for forwarding requests to and from a
    kubernetes' local docker proxy. In case of any errors during creating the
    process - throws a RuntimeError exception with a short description of
    a cause of a problem.
    When proxy created by this function is no longer needed - it should
    be closed by calling kill() function on a process returned by this
    function.

    :return:
        instance of a process with proxy
    """
    logger.debug("Start port forwarding")
    process = None

    try:
        t_registry_pod_name, exit_code = execute_system_command(GETTING_POD_NAME_COMMAND)
        registry_pod_name = None

        if t_registry_pod_name and not exit_code:
            # pod name taken this way contains \n at the end - so it has to be removed
            registry_pod_name = t_registry_pod_name.strip("\n")
        else:
            logger.error("Port forwarding - exception - missing pod name : {}".format(
                t_registry_pod_name if t_registry_pod_name else "missing data"
            ))
            raise KubectlIntError("Missing pod name during creation of registry port proxy.")

        t_registry_port, exit_code = execute_system_command(GETTING_PORT_COMMAND)
        registry_port = None

        if t_registry_port and not exit_code and t_registry_port.isdigit():
            # pod name taken this way contains \n at the end - so it has to be removed
            registry_port = t_registry_port
        else:
            logger.error("Port forwarding - exception - missing pod port : {}".format(
                t_registry_port if t_registry_port else "missing data"
            ))
            raise KubectlIntError("Missing pod port during creation of registry port proxy.")

        dc_output, dc_exit_code = set_registry_port(registry_port)

        if dc_exit_code:
            logger.error("Port forwarding - exception - setting draft config failed : {}".format(
                dc_output
            ))
            raise KubectlIntError("Setting draft config failed.")

        PORT_FORWARD_COMMAND = ["kubectl", "port-forward", "--namespace={}".format(NAMESPACE),
                                registry_pod_name, "{}:{}".format(registry_port, DOCKER_PORT)]

        # if a log level is set to DEBUG - additional information from creatoin of a proxy
        # are sent to console
        std_output = subprocess.DEVNULL
        if is_debug_level(logger):
            std_output = subprocess.STDOUT

        process = subprocess.Popen(args=PORT_FORWARD_COMMAND, stdout=std_output, stderr=std_output)

        if not process:
            logger.error("Port forwarding - exception - process doesn't exist.")
            raise KubectlIntError("Registry port proxy hasn't been created.")

    except KubectlIntError as exe:
        raise RuntimeError(exe)
    except Exception as exe:
        logger.exception("Port forwarding - exception - other.")
        raise RuntimeError("Other error during creation of registry port proxy.")

    logger.debug("Port forwarding - proxy set up.")
    return process
