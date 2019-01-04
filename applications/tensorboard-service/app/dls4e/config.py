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

from typing import Dict

from kubernetes import client, config
from kubernetes.client import V1ConfigMap

DLS4E_CONFIG_CONFIGMAP_NAME = 'dls4enterprise'
DLS4E_CONFIG_CONFIGMAP_NAMESPACE = 'dls4e'

DLS4E_CONFIG_TENSORBOARD_TIMEOUT = 'tensorboard.timeout'
DLS4E_DEFAULT_TENSORBOARD_TIMEOUT = '1800'


class Dls4ePlatformConfig:
    def __init__(self, k8s_api_client: client.CoreV1Api):
        self.client = k8s_api_client

    @classmethod
    def incluster_init(cls):
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        return cls(k8s_api_client=v1)

    def _fetch_platform_configmap(self) -> Dict[str, str]:
        configmap: V1ConfigMap = self.client.read_namespaced_config_map(name=DLS4E_CONFIG_CONFIGMAP_NAME,
                                                                        namespace=DLS4E_CONFIG_CONFIGMAP_NAMESPACE)

        configmap_data: Dict[str, str] = configmap.data

        return configmap_data

    def get_tensorboard_image(self) -> str:
        data = self._fetch_platform_configmap()
        return f"{data['registry']}/{data['image.tensorflow']}"

    def get_activity_proxy_image(self) -> str:
        data = self._fetch_platform_configmap()
        return f"{data['registry']}/{data['image.activity-proxy']}"

    def get_tensorboard_timeout(self):
        data = self._fetch_platform_configmap()
        if data.get(DLS4E_CONFIG_TENSORBOARD_TIMEOUT):
            return data.get(DLS4E_CONFIG_TENSORBOARD_TIMEOUT)
        return DLS4E_CONFIG_TENSORBOARD_TIMEOUT
