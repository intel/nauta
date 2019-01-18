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


from unittest.mock import MagicMock

from kubernetes.client import V1ConfigMap
import pytest

from nauta.config import NautaPlatformConfig


fake_cm = V1ConfigMap(
    data={
        'registry': '127.0.0.1:30303',
        'image.activity-proxy': 'activity-proxy:dev',
        'image.tensorflow': 'nauta/tensorflow/1.9.0py3/haswell/base:1.9.0-py3'
    }
)


@pytest.fixture
def nauta_platform_config_mocked():
    # noinspection PyTypeChecker
    config = NautaPlatformConfig(k8s_api_client=MagicMock())

    return config


def test_incluster_init(mocker):
    mocker.patch('nauta.config.config')

    nauta_config = NautaPlatformConfig.incluster_init()

    assert nauta_config
    assert nauta_config.client


# noinspection PyShadowingNames
def test_fetch_platform_configmap(mocker, nauta_platform_config_mocked: NautaPlatformConfig):
    mocker.patch.object(nauta_platform_config_mocked.client, 'read_namespaced_config_map').return_value = fake_cm

    # noinspection PyProtectedMember
    configmap_dict = nauta_platform_config_mocked._fetch_platform_configmap()

    assert configmap_dict == fake_cm.data


# noinspection PyShadowingNames
def test_get_tensorboard_image(mocker, nauta_platform_config_mocked: NautaPlatformConfig):
    mocker.patch.object(nauta_platform_config_mocked, '_fetch_platform_configmap').return_value = fake_cm.data

    tb_image = nauta_platform_config_mocked.get_tensorboard_image()

    assert tb_image == '127.0.0.1:30303/nauta/tensorflow/1.9.0py3/haswell/base:1.9.0-py3'


# noinspection PyShadowingNames
def test_get_activity_proxy_image(mocker, nauta_platform_config_mocked: NautaPlatformConfig):
    mocker.patch.object(nauta_platform_config_mocked, '_fetch_platform_configmap').return_value = fake_cm.data

    ap_image = nauta_platform_config_mocked.get_activity_proxy_image()

    assert ap_image == '127.0.0.1:30303/activity-proxy:dev'
