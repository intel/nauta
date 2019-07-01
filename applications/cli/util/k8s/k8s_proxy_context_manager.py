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

import socket
import threading

import requests
from requests.exceptions import ConnectionError
import time

import psutil
from urllib3.exceptions import NewConnectionError

from util.k8s import kubectl
from util.app_names import NAUTAAppNames
from util.logger import initialize_logger
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError, KubectlConnectionError
from cli_text_consts import UtilK8sProxyTexts as Texts

logger = initialize_logger(__name__)


class TunnelSetupError(RuntimeError):
    pass


class K8sProxy:
    def __init__(self, nauta_app_name: NAUTAAppNames, port: int = None,
                 app_name: str = None, number_of_retries: int = 0, namespace: str = None,
                 number_of_retries_wait_for_readiness: int = 30):
        self.nauta_app_name = nauta_app_name
        self.external_port = port
        self.app_name = app_name
        self.number_of_retries = number_of_retries
        self.namespace = namespace
        self.number_of_retries_wait_for_readiness = number_of_retries_wait_for_readiness
        self.tunnel_monitor_thread = None

    def __enter__(self):
        logger.debug("k8s_proxy - entering")
        try:
            self.process, self.tunnel_port, self.container_port \
                = kubectl.start_port_forwarding(k8s_app_name=self.nauta_app_name,
                                                port=self.external_port,
                                                app_name=self.app_name,
                                                number_of_retries=self.number_of_retries,
                                                namespace=self.namespace)
            self.tunnel_monitor_thread = threading.Thread(target=self._log_tunnel_output, args=(self.process,))
            self.tunnel_monitor_thread.start()
            try:
                self._wait_for_connection_readiness('127.0.0.1', self.tunnel_port,
                                                    tries=self.number_of_retries_wait_for_readiness)
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
            except (ConnectionError, NewConnectionError) as e:
                error_msg = f'can not connect to {address}:{port}. Error: {e}'
                logger.exception(error_msg) if retry == tries-1 else logger.debug(error_msg)  # type: ignore
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

        if self.tunnel_monitor_thread:
            self.tunnel_monitor_thread.join(timeout=10)

    @staticmethod
    def _log_tunnel_output(tunnel_process):
        for stdout_line in iter(tunnel_process.stdout.readline, ''):
            logger.debug('Tunnel({pid}) STDOUT: {line}'.format(line=stdout_line, pid=tunnel_process.pid))


class TcpK8sProxy(K8sProxy):
    def __init__(self, nauta_app_name: NAUTAAppNames, port: int = None,
                 app_name: str = None, number_of_retries: int = 0, namespace: str = None):
        super().__init__(nauta_app_name=nauta_app_name, port=port, app_name=app_name,
                         number_of_retries=number_of_retries, namespace=namespace)

    @staticmethod
    def _wait_for_connection_readiness(address: str, port: int, tries: int = 30):
        sock = None
        for retry in range(tries):
            try:
                sock = socket.create_connection((address, port))
                break
            except (ConnectionError, ConnectionRefusedError) as e:
                error_msg = f'can not connect to {address}:{port}. Error: {e}'
                logger.exception(error_msg) if retry == tries - 1 else logger.debug(error_msg)  # type: ignore
                time.sleep(1)
            finally:
                if sock:
                    sock.close()
        else:
            raise TunnelSetupError(Texts.TUNNEL_NOT_READY_ERROR_MSG.format(address=address, port=port))


def check_port_forwarding():
    with K8sProxy(NAUTAAppNames.WEB_GUI) as proxy:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = "127.0.0.1", proxy.tunnel_port
        if sock.connect_ex(address) != 0:
            raise KubectlConnectionError(Texts.K8S_PORT_FORWARDING_ERROR_MSG)
