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
from typing import Dict

# environmental variable with a dlsctl HOME folder
DLS_CTL_CONFIG_ENV_NAME = 'DLS_CTL_CONFIG'
DLS_CTL_CONFIG_DIR_NAME = 'dls_ctl_config'

# name of a directory with EXPERIMENT's data
EXPERIMENTS_DIR_NAME = 'experiments'


class Fields(Enum):
    CONFIG_PATH = 'config_path'


class DLS4EConfigMapFields(Enum):
    IMAGE_TILLER = 'image.tiller'
    EXTERNAL_IP = "external_ip"


class Config:
    __params = dict()

    @staticmethod
    def get(field: Fields):
        return Config.__params.get(field.value)

    @staticmethod
    def set(field: Fields, value):
        Config.__params[field.value] = value


class DLS4EConfigMap:
    _params = dict()

    @staticmethod
    def get(field: DLS4EConfigMapFields):
        return DLS4EConfigMap._params[field.value]

    @staticmethod
    def set(field: DLS4EConfigMapFields, value):
        DLS4EConfigMap._params[field.value] = value

    @staticmethod
    def init(data: Dict[str, str]):
        DLS4EConfigMap._params = data
