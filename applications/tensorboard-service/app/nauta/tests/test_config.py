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
