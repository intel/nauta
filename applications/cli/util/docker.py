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

import requests
from http import HTTPStatus
from typing import List

from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.logger import initialize_logger
from util.app_names import NAUTAAppNames
from cli_text_consts import UtilDockerTexts as Texts


logger = initialize_logger(__name__)


def get_tags_list(server_address: str, image_name: str) -> List[str]:
    """
    Returns list of tags connected with an image with a given name
    :param server_address: address of a server with docker registry
    :param image_name: name of an image
    :return: list of tags connected with a given image
    In case of any problems during getting list of tags - it throws an error
    """
    url = f"http://{server_address}/v2/{image_name}/tags/list"
    result = requests.get(url)

    if not result or result.status_code != HTTPStatus.OK:
        err_message = Texts.TAGS_GET_ERROR_MSG
        logger.exception(err_message)
        raise RuntimeError(err_message)

    return result.json().get("tags")


def delete_tag(server_address: str, image_name: str, tag: str):
    """
    Deletes image with a given name and tag. To perform a final removal it needs garbage collection
    to be performed on registry.
    :param server_address: address of a server with docker registry
    :param image_name: name of an image
    :param tag: id of the tag which should be deleted
     In case of any problems during deletion of a tag it raises an exception
    """
    get_digest_url = f"http://{server_address}/v2/{image_name}/manifests/{tag}"
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    result = requests.get(get_digest_url, headers=headers)

    if not result or result.status_code != HTTPStatus.OK or not result.headers.get("Docker-Content-Digest"):
        err_message = Texts.IMAGE_DELETE_ERROR_MSG
        logger.exception(err_message)
        raise RuntimeError(err_message)

    digest = result.headers.get("Docker-Content-Digest")

    if not digest:
        err_message = Texts.IMAGE_DELETE_ERROR_MSG
        logger.exception(err_message)
        raise RuntimeError(err_message)

    delete_tag_url = f"http://{server_address}/v2/{image_name}/manifests/{digest}"
    result = requests.delete(delete_tag_url, headers=headers)

    if not result or result.status_code != HTTPStatus.ACCEPTED:
        err_message = Texts.IMAGE_DELETE_ERROR_MSG
        logger.exception(err_message)
        raise RuntimeError(err_message)


def delete_images_for_experiment(exp_name: str):
    """
    Deletes image related to experiment with a given name.
    :param exp_name: name of an experiment for which image should be removed
    In case of any problems it raises an error
    """
    with K8sProxy(NAUTAAppNames.DOCKER_REGISTRY) as proxy:
        # Save port that was actually used in configuration
        server_address = f"127.0.0.1:{proxy.tunnel_port}"
        list_of_tags = get_tags_list(server_address=server_address, image_name=exp_name)

        for tag in list_of_tags:
            delete_tag(server_address=server_address, image_name=exp_name, tag=tag)
