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
