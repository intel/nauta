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
import sys
from typing import Optional

import yaml

from util.k8s.k8s_info import get_config_map_data
from util.logger import initialize_logger

# environmental variable with a dlsctl HOME folder
DLS_CTL_CONFIG_ENV_NAME = 'DLS_CTL_CONFIG'
DLS_CTL_CONFIG_DIR_NAME = 'dls_ctl_config'

# name of a directory with EXPERIMENT's data
EXPERIMENTS_DIR_NAME = 'experiments'
# name of a directory with data copied from script folder location
FOLDER_DIR_NAME = 'folder'

# registry config file
DOCKER_REGISTRY_CONFIG_FILE = 'docker_registry.yaml'

DLS4E_NAMESPACE = "dls4e"
DLS4E_CONFIGURATION_CM = "dls4enterprise"


log = initialize_logger(__name__)


class ConfigInitError(Exception):
    def __init__(self, message: str):
        self.message = message


class Config:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'config_path'):
            self.config_path = self.get_config_path()

    @classmethod
    def get_config_path(self) -> str:
        binary_config_dir_path = os.path.join(os.path.dirname(sys.executable), DLS_CTL_CONFIG_DIR_NAME)
        user_local_config_dir_path = os.path.join(os.path.expanduser('~'), DLS_CTL_CONFIG_DIR_NAME)

        log.debug(f"{DLS_CTL_CONFIG_DIR_NAME} binary executable path:  {binary_config_dir_path}")
        log.debug(f'{DLS_CTL_CONFIG_DIR_NAME} user home path:  {binary_config_dir_path}')

        if DLS_CTL_CONFIG_ENV_NAME in os.environ and os.environ.get(DLS_CTL_CONFIG_ENV_NAME):
            user_path = os.environ.get(DLS_CTL_CONFIG_ENV_NAME)
            if os.path.exists(user_path):
                return user_path
            else:
                message = f'Cannot find {user_path} directory from {DLS_CTL_CONFIG_ENV_NAME} env!'
                raise ConfigInitError(message)
        elif user_local_config_dir_path and os.path.exists(user_local_config_dir_path):
            return user_local_config_dir_path
        elif binary_config_dir_path and os.path.exists(binary_config_dir_path):
            return binary_config_dir_path
        else:
            message = f'Cannot find {DLS_CTL_CONFIG_DIR_NAME} directory in {binary_config_dir_path} and ' \
                      f'{user_local_config_dir_path}. Use {DLS_CTL_CONFIG_ENV_NAME} env to point ' \
                      f'{DLS_CTL_CONFIG_DIR_NAME} directory location'
            raise ConfigInitError(message)

    @property
    def local_registry_port(self) -> Optional[int]:
        docker_registry_config_file_path = os.path.join(self.config_path, DOCKER_REGISTRY_CONFIG_FILE)
        if not os.path.isfile(docker_registry_config_file_path):
            log.debug(f'Docker registry config file not found ({docker_registry_config_file_path}).')
            return None

        with open(docker_registry_config_file_path, mode='r', encoding='utf-8') as docker_registry_config_file:
            docker_registry_config = yaml.load(docker_registry_config_file) or {}

        return docker_registry_config.get('local_registry_port')

    @local_registry_port.setter
    def local_registry_port(self, port: int):
        docker_registry_config_file_path = os.path.join(self.config_path, DOCKER_REGISTRY_CONFIG_FILE)
        log.debug(f'Saving local registry port ({port}) to {docker_registry_config_file_path}.')

        with open(docker_registry_config_file_path, mode='w+', encoding='utf-8') as docker_registry_config_file:
            docker_registry_config = yaml.load(docker_registry_config_file) or {}
            docker_registry_config['local_registry_port'] = port
            yaml.dump(docker_registry_config, docker_registry_config_file, default_flow_style=False)


class DLS4EConfigMap:
    """
    Class for accessing values stored in DLS4E config map on Kubernetes cluster.
    It is implemented using borg pattern (http://code.activestate.com/recipes/66531/),
    so each instance of this class will have shared state, ensuring configuration consistency.
    """
    IMAGE_TILLER_FIELD = 'image.tiller'
    EXTERNAL_IP_FIELD = 'external_ip'
    IMAGE_TENSORBOARD_SERVICE_FIELD = 'image.tensorboard_service'
    REGISTRY_FIELD = 'registry'
    PLATFORM_VERSION = 'platform.version'
    PY2_IMAGE_NAME = 'image.tensorflow_1.9_py2'
    PY3_IMAGE_NAME = 'image.tensorflow_1.9_py3'

    __shared_state = {}

    def __init__(self, config_map_request_timeout: int = None):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'image_tiller') or not hasattr(self, 'external_ip') \
                or not hasattr(self, 'image_tensorboard_service') or not hasattr(self, "platform.version"):
            config_map_data = get_config_map_data(name=DLS4E_CONFIGURATION_CM, namespace=DLS4E_NAMESPACE,
                                                  request_timeout=config_map_request_timeout)
            self.image_tiller = '{}/{}'.format(config_map_data[self.REGISTRY_FIELD],
                                               config_map_data[self.IMAGE_TILLER_FIELD])
            self.external_ip = config_map_data[self.EXTERNAL_IP_FIELD]
            self.image_tensorboard_service = '{}/{}'.format(config_map_data[self.REGISTRY_FIELD],
                                                            config_map_data[self.IMAGE_TENSORBOARD_SERVICE_FIELD])
            self.platform_version = config_map_data.get(self.PLATFORM_VERSION)
            self.py2_image_name = config_map_data.get(self.PY2_IMAGE_NAME)
            self.py3_image_name = config_map_data.get(self.PY3_IMAGE_NAME)
