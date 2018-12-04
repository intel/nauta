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

import socket

import requests
from requests.exceptions import ConnectionError
import time

import psutil

from util.config import Config
from util.k8s import kubectl
from util.app_names import DLS4EAppNames
from util.logger import initialize_logger
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError, KubectlConnectionError
from cli_text_consts import UtilK8sProxyTexts as Texts

logger = initialize_logger(__name__)


class TunnelSetupError(RuntimeError):
    pass


class K8sProxy:
    def __init__(self, dls4e_app_name: DLS4EAppNames, port: int = None,
                 app_name: str = None, number_of_retries: int = 0, namespace: str = None):
        self.dls4e_app_name = dls4e_app_name
        self.external_port = port
        self.app_name = app_name
        self.number_of_retries = number_of_retries
        self.namespace = namespace

    def __enter__(self):
        logger.debug("k8s_proxy - entering")
        try:
            self.process, self.tunnel_port, self.container_port \
                = kubectl.start_port_forwarding(k8s_app_name=self.dls4e_app_name,
                                                port=self.external_port,
                                                app_name=self.app_name,
                                                number_of_retries=self.number_of_retries,
                                                namespace=self.namespace)
            try:
                K8sProxy._wait_for_connection_readiness('localhost', self.tunnel_port)
            except Exception as ex:
                self._close_tunnel()
                raise ex
        except LocalPortOccupiedError as exe:
            raise exe
        except Exception as exe:
            error_message = Texts.PROXY_ENTER_ERROR_MSG
            logger.exception(error_message)
            raise K8sProxyOpenError(error_message) from exe

        return self

    def __exit__(self, *args):
        logger.debug("k8s_proxy - exiting")
        try:
            self._close_tunnel()
        except psutil.NoSuchProcess:
            logger.debug(Texts.TUNNEL_ALREADY_CLOSED)
        except Exception as exe:
            error_message = Texts.PROXY_EXIT_ERROR_MSG
            logger.exception(error_message)
            raise K8sProxyCloseError(error_message) from exe

    @staticmethod
    def _wait_for_connection_readiness(address: str, port: int, tries: int = 30):
        for retry in range(tries):
            try:
                requests.get(f'http://{address}:{port}')
                return
            except ConnectionError as e:
                error_msg = f'can not connect to {address}:{port}. Error: {e}'
                logger.exception(error_msg) if retry == tries-1 else logger.debug(error_msg)
                time.sleep(1)
        raise TunnelSetupError(Texts.TUNNEL_NOT_READY_ERROR_MSG.format(address=address, port=port))

    def _close_tunnel(self):
        children = psutil.Process(self.process.pid).children(recursive=True)
        children.insert(0, self.process)
        for child in children:
            child.terminate()
        gone, alive = psutil.wait_procs(children, timeout=3)
        for survivor in alive:
            survivor.kill()


def check_port_forwarding():
    config = Config()
    with K8sProxy(DLS4EAppNames.DOCKER_REGISTRY, port=config.local_registry_port) as proxy:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = "127.0.0.1", proxy.tunnel_port
        if sock.connect_ex(address) != 0:
            raise KubectlConnectionError(Texts.K8S_PORT_FORWARDING_ERROR_MSG)
