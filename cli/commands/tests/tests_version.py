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

import pytest
from kubernetes.client.models import V1ConfigMap
from click.testing import CliRunner

from commands import version
from version import VERSION
from util.config import DLS4EConfigMap

PLATFORM_VERSION = "1.2"


@pytest.fixture()
def mocked_k8s_CoreV1Api(mocker):
    mocked_coreV1Api_class = mocker.patch('kubernetes.client.CoreV1Api')
    mocker.patch('kubernetes.client.ApiClient')
    coreV1API_instance = mocked_coreV1Api_class.return_value

    v1_config_map = V1ConfigMap(data={DLS4EConfigMap.PLATFORM_VERSION: PLATFORM_VERSION,
                                      DLS4EConfigMap.IMAGE_TILLER_FIELD: "",
                                      DLS4EConfigMap.EXTERNAL_IP_FIELD: "",
                                      DLS4EConfigMap.IMAGE_TENSORBOARD_SERVICE_FIELD: "",
                                      DLS4EConfigMap.REGISTRY_FIELD: ""})

    coreV1API_instance.read_namespaced_config_map.return_value = v1_config_map

    return coreV1API_instance


def test_version(mocked_k8s_CoreV1Api):
    runner = CliRunner()
    result = runner.invoke(version.version, [])

    assert f"dlsctl application version: {VERSION}" in result.output
    assert f"dls4e platform version: {PLATFORM_VERSION}" in result.output
