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

from time import sleep
from typing import Optional

import docker
from docker.errors import NotFound
from docker.models.containers import Container

client = docker.from_env()

SOCAT_CONTAINER_NAME_PREFIX = 'dlsctl-registry-bridge'

socat_container_name = 'socat-'


def get() -> Optional[Container]:
    try:
        socat_container = client.containers.get(socat_container_name)  # type: Container
        if socat_container.status != 'running':
            socat_container.remove(force=True)
            return None
    except NotFound:
        return None

    return socat_container


def _ensure_socat_running():
    for _ in range(120):
        try:
            socat_container = client.containers.get(socat_container_name)
        except NotFound:
            sleep(1)
            continue

        if socat_container.status == 'running':
            return

        sleep(1)

    raise RuntimeError(f"failed to start socat container! expected status: 'running', got: {socat_container.status}")


def start(docker_registry_port: str):
    """
    This function is synchronous - it returns when socat container is running.
    :param docker_registry_port:
    :return:
    """
    global socat_container_name
    socat_container_name = f'{SOCAT_CONTAINER_NAME_PREFIX}-{docker_registry_port}'

    # TODO: change image to socat from cluster instead public Internet
    client.containers.run(detach=True, remove=True, network_mode='host', name=socat_container_name,
                          image='alpine/socat', command=f'TCP-LISTEN:{docker_registry_port},fork,reuseaddr '
                                                        f'TCP:host.docker.internal:{docker_registry_port}')

    _ensure_socat_running()


def stop():
    socat_container = get()
    if socat_container:
        socat_container.stop()
