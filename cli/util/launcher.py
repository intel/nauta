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

import webbrowser
import click

from kubernetes import config
from kubernetes.client import configuration
from util.system import get_current_os, OS
from util import socat
from util.network import wait_for_connection
from util.logger import initialize_logger

from util.app_names import DLS4EAppNames
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError, LaunchError, \
    ProxyClosingError


logger = initialize_logger(__name__)

FORWARDED_URL = 'http://localhost:{}{}'


def is_gui_browser_available() -> bool:
    try:
        browser = webbrowser.get()
        return True if type(browser) not in {webbrowser.GenericBrowser, None} else False
    except webbrowser.Error:
        logger.exception('Failed to get webbrowser.')
        return False


def launch_app(k8s_app_name: DLS4EAppNames = None, no_launch: bool = False, port: int = None, app_name: str = None,
               number_of_retries: int = 0, url_end: str = "", namespace: str = None):
    try:
        with K8sProxy(dls4e_app_name=k8s_app_name, port=port, app_name=app_name,
                      number_of_retries=number_of_retries, namespace=namespace) as proxy:
            url = FORWARDED_URL.format(proxy.tunnel_port, url_end)
            # run socat if on Windows or Mac OS
            if get_current_os() in (OS.WINDOWS, OS.MACOS):
                # noinspection PyBroadException
                try:
                    socat.start(proxy.container_port)
                except Exception:
                    err_message = 'Error during creation of a local docker-host tunnel.'
                    logger.exception(err_message)
                    raise LaunchError(err_message)

            if k8s_app_name == DLS4EAppNames.INGRESS:
                config.load_kube_config()
                user_token = configuration.Configuration().api_key.get('authorization')
                prepared_user_token = user_token.replace('Bearer ', '')
                url = f'{url}?token={prepared_user_token}'

            if not no_launch:
                if is_gui_browser_available():
                    click.echo('Browser will start in few seconds. Please wait... ')
                    wait_for_connection(url)
                    webbrowser.open_new(url)
                else:
                    err_message = 'Cannot find a suitable web browser. Try running this command ' \
                                  'with --no-launch option.'

                    raise LaunchError(err_message)

            click.echo('Go to {}'.format(url))

            input('Proxy connection created.\nPress ENTER key to close a port forwarding process...')
    except K8sProxyCloseError:
        err_message = 'Error during closing of a proxy for a {}'.format(k8s_app_name)
        raise ProxyClosingError(err_message)
    except LocalPortOccupiedError as exe:
        err_message = 'Error during creation of a proxy for a {}. {}'.format(k8s_app_name, exe.message)
        raise LaunchError(err_message)
    except K8sProxyOpenError:
        error_msg = 'Error during creation of a proxy for a {}'
        logger.exception(error_msg.format(k8s_app_name))
        raise LaunchError(error_msg.format(k8s_app_name))
    except Exception:
        err_message = 'Failed to launch web application.'
        logger.exception(err_message)
        raise LaunchError(err_message)
    finally:
        # noinspection PyBroadException
        # terminate socat if on Windows or Mac OS
        if get_current_os() in (OS.WINDOWS, OS.MACOS):
            # noinspection PyBroadException
            try:
                socat.stop()
            except Exception:
                err_message = 'Error during closing of a proxy for a {}'.format(k8s_app_name)
                raise ProxyClosingError(err_message)
