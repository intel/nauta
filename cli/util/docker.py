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

import requests
from http import HTTPStatus
from typing import List

from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.logger import initialize_logger
from util.app_names import DLS4EAppNames

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
        err_message = "Error during getting list of tags for an image."
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
        err_message = "Error during deletion of an image."
        logger.exception(err_message)
        raise RuntimeError(err_message)

    digest = result.headers.get("Docker-Content-Digest")

    if not digest:
        err_message = "Error during deletion of an image."
        logger.exception(err_message)
        raise RuntimeError(err_message)

    delete_tag_url = f"http://{server_address}/v2/{image_name}/manifests/{digest}"
    result = requests.delete(delete_tag_url, headers=headers)

    if not result or result.status_code != HTTPStatus.ACCEPTED:
        err_message = "Error during deletion of an image."
        logger.exception(err_message)
        raise RuntimeError(err_message)


def delete_images_for_experiment(exp_name: str):
    """
    Deletes image related to experiment with a given name.
    :param exp_name: name of an experiment for which image should be removed
    In case of any problems it raises an error
    """
    with K8sProxy(DLS4EAppNames.DOCKER_REGISTRY) as proxy:
        # Save port that was actually used in configuration
        server_address = f"127.0.0.1:{proxy.tunnel_port}"
        list_of_tags = get_tags_list(server_address=server_address, image_name=exp_name)

        for tag in list_of_tags:
            delete_tag(server_address=server_address, image_name=exp_name, tag=tag)
