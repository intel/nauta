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

import os
import random
import string
from time import sleep
from typing import Optional

import docker
from docker.errors import NotFound
from docker.models.containers import Container
from cli_text_consts import UtilSocatTexts as Texts
from util.config import Config


client = docker.from_env()

SOCAT_CONTAINER_NAME_PREFIX = 'nctl-registry-bridge'

socat_container_name = 'socat-'

SOCAT_IMAGE_FILE_NAME = 'socat-container-image.tar.gz'

SOCAT_IMAGE_NAME = 'socat-container-image:latest'


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

    raise RuntimeError(Texts.SOCAT_CONTAINER_START_FAIL_MSG.format(container_status=socat_container.status))


def load_socat_image():
    config = Config()
    if config.config_path and not client.images.list(name=SOCAT_IMAGE_NAME):
        with open(os.path.join(config.config_path, SOCAT_IMAGE_FILE_NAME), "rb") as file:
            client.images.load(file)

        if not client.images.list(name=SOCAT_IMAGE_NAME):
            raise RuntimeError


def start(docker_registry_port: str):
    """
    This function is synchronous - it returns when socat container is running.
    :param docker_registry_port:
    :return:
    """
    global socat_container_name
    random_part = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                          for _ in range(5))
    socat_container_name = f'{SOCAT_CONTAINER_NAME_PREFIX}-{random_part}-' \
                           f'{docker_registry_port}'
    load_socat_image()
    client.containers.run(detach=True, remove=True, network_mode='host', name=socat_container_name,
                          image=SOCAT_IMAGE_NAME, command=f'{docker_registry_port}')

    _ensure_socat_running()


def stop():
    socat_container = get()
    if socat_container:
        socat_container.stop()
