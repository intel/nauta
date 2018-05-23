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

from enum import Enum

from util.k8s.k8s_info import get_config_map_data

# environmental variable with a dlsctl HOME folder
DLS_CTL_CONFIG_ENV_NAME = 'DLS_CTL_CONFIG'
DLS_CTL_CONFIG_DIR_NAME = 'dls_ctl_config'

# name of a directory with EXPERIMENT's data
EXPERIMENTS_DIR_NAME = 'experiments'

DLS4E_NAMESPACE = "dls4e"
DLS4E_CONFIGURATION_CM = "dls4enterprise"


class Fields(Enum):
    CONFIG_PATH = 'config_path'


class Config:
    __params = dict()

    @staticmethod
    def get(field: Fields):
        return Config.__params.get(field.value)

    @staticmethod
    def set(field: Fields, value):
        Config.__params[field.value] = value


class DLS4EConfigMap:
    """
    Class for accessing values stored in DLS4E config map on Kubernetes cluster.
    It is implemented using borg pattern (http://code.activestate.com/recipes/66531/),
    so each instance of this class will have shared state, ensuring configuration consistency.
    """
    IMAGE_TILLER_FIELD = 'image.tiller'
    EXTERNAL_IP_FIELD = 'external_ip'

    __shared_state = {}
    image_tiller: str = None
    external_ip: str = None

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.image_tiller or not self.external_ip:
            config_map_data = get_config_map_data(name=DLS4E_CONFIGURATION_CM, namespace=DLS4E_NAMESPACE)
            self.image_tiller = config_map_data[self.IMAGE_TILLER_FIELD]
            self.external_ip = config_map_data[self.EXTERNAL_IP_FIELD]
