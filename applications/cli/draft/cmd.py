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
