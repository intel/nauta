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

import signal
import requests
from requests.exceptions import ConnectionError
import time

import psutil

from util.k8s import kubectl
from util.app_names import DLS4EAppNames
from util.logger import initialize_logger
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.system import get_current_os, OS
from cli_text_consts import UTIL_K8S_PROXY_TEXTS as TEXTS


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
            error_message = TEXTS["proxy_enter_error_msg"]
            logger.exception(error_message)
            raise K8sProxyOpenError(error_message) from exe

        return self

    def __exit__(self, *args):
        logger.debug("k8s_proxy - exiting")
        try:
            self._close_tunnel()
        except Exception as exe:
            error_message = TEXTS["proxy_exit_error_msg"]
            logger.exception(error_message)
            raise K8sProxyCloseError(error_message) from exe

    @staticmethod
    def _wait_for_connection_readiness(address: str, port: int, tries: int = 30):
        for _ in range(tries):
            try:
                requests.get(f'http://{address}:{port}')
                return
            except ConnectionError as e:
                logger.error(f'can not connect to {address}:{port}. Error: {e}')
                time.sleep(1)
        raise TunnelSetupError(TEXTS["tunnel_not_ready_error_msg"].format(address=address, port=port))

    def _close_tunnel(self):
        if get_current_os() == OS.WINDOWS:
            self.process.terminate()
        else:
            for proc in psutil.Process(self.process.pid).children(recursive=True):
                proc.send_signal(signal.SIGTERM)
            self.process.send_signal(signal.SIGKILL)

        self.process.wait()
