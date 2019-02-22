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
from typing import Tuple

import docker
from retry.api import retry_call
from requests.exceptions import ConnectionError

from cli_text_consts import DraftCmdTexts as Texts
from util import helm
from util.config import Config
from util.filesystem import copytree_content
from util.logger import initialize_logger

logger = initialize_logger('draft.cmd')

DOCKER_CONNECTION_MAX_TRIES = 100
DOCKER_CONNECTION_DELAY_SECONDS = 5


class NoPackError(Exception):
    pass


def create(working_directory: str = None, pack_type: str = None) -> Tuple[str, int]:
    try:
        config_dirpath = Config().get_config_path()

        packs_dirpath = os.path.join(config_dirpath, 'packs')

        requested_pack_path = os.path.join(packs_dirpath, pack_type)

        if not os.path.isdir(requested_pack_path):
            raise NoPackError(f'no pack found with name: {requested_pack_path}')

        helm_chart_destination_dirpath = f"{working_directory}/charts/{pack_type}"
        os.makedirs(helm_chart_destination_dirpath)

        copytree_content(f"{requested_pack_path}", f"{working_directory}", ignored_objects=['charts'])
        copytree_content(f"{requested_pack_path}/charts", helm_chart_destination_dirpath)
    except NoPackError as ex:
        # TODO: these exceptions should be reraised instead caught here
        logger.exception(ex)
        return Texts.PACK_NOT_EXISTS, 1
    except Exception as ex:
        logger.exception(ex)
        return Texts.DEPLOYMENT_NOT_CREATED, 100

    return "", 0


def up(run_name: str, local_registry_port: int, working_directory: str = None, namespace: str = None) -> \
        Tuple[str, int]:
    try:
        docker_client = docker.from_env()
        # we've seen often a problems with connection to local Docker's daemon via socket.
        # here we retry a call to Docker in case of such problems
        # original call without retry_call:
        # docker_client.images.build(path=working_directory, tag=f"127.0.0.1:{local_registry_port}/{run_name}")
        retry_call(f=docker_client.images.build,
                   fkwargs={"path": working_directory, "tag": f"127.0.0.1:{local_registry_port}/{run_name}"},
                   exceptions=ConnectionError,
                   tries=DOCKER_CONNECTION_MAX_TRIES,
                   delay=DOCKER_CONNECTION_DELAY_SECONDS
                   )
    except Exception as ex:
        # TODO: these exceptions should be reraised instead caught here
        logger.exception(ex)
        return Texts.DOCKER_IMAGE_NOT_BUILT, 100

    try:
        # we've seen often a problems with connection to local Docker's daemon via socket.
        # here we retry a call to Docker in case of such problems
        # original call without retry_call:
        # docker_client.images.push(repository=f"127.0.0.1:{local_registry_port}/{run_name}")
        retry_call(f=docker_client.images.push,
                   fkwargs={"repository": f"127.0.0.1:{local_registry_port}/{run_name}"},
                   exceptions=ConnectionError,
                   tries=DOCKER_CONNECTION_MAX_TRIES,
                   delay=DOCKER_CONNECTION_DELAY_SECONDS
                   )
    except Exception as ex:
        logger.exception(ex)
        return Texts.DOCKER_IMAGE_NOT_SENT, 101

    try:
        dirs = os.listdir(f"{working_directory}/charts")
        helm.install_helm_chart(f"{working_directory}/charts/{dirs[0]}",
                                release_name=run_name,
                                tiller_namespace=namespace)
    except Exception as ex:
        logger.exception(ex)
        return Texts.APP_NOT_RELEASED, 102

    return "", 0
