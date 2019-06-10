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

import webbrowser

import click
from kubernetes import config
from kubernetes.client import configuration

from util.spinner import spinner
from util.network import wait_for_connection
from util.logger import initialize_logger
from util.system import wait_for_ctrl_c
from util.app_names import NAUTAAppNames
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError, LaunchError, \
    ProxyClosingError
from cli_text_consts import UtilLauncherTexts as Texts

logger = initialize_logger(__name__)

FORWARDED_URL = 'http://localhost:{}{}'


def is_gui_browser_available() -> bool:
    try:
        browser = webbrowser.get()
        return True if type(browser) not in {webbrowser.GenericBrowser, None} else False
    except webbrowser.Error:
        logger.exception('Failed to get webbrowser.')
        return False


def launch_app(k8s_app_name: NAUTAAppNames, no_launch: bool = False, port: int = None, app_name: str = None,
               number_of_retries: int = 0, url_end: str = "", namespace: str = None):
    try:
        with spinner(text=Texts.LAUNCHING_APP_MSG) as proxy_spinner, \
             K8sProxy(nauta_app_name=k8s_app_name, port=port, app_name=app_name,
                      number_of_retries=number_of_retries, namespace=namespace) as proxy:
            url = FORWARDED_URL.format(proxy.tunnel_port, url_end)

            if k8s_app_name == NAUTAAppNames.INGRESS:
                config.load_kube_config()
                user_token = configuration.Configuration().api_key.get('authorization')
                prepared_user_token = user_token.replace('Bearer ', '')
                url = f'{url}?token={prepared_user_token}'

            if not no_launch:

                if is_gui_browser_available():
                    wait_for_connection(url)
                    webbrowser.open_new(url)
                    proxy_spinner.hide()
                else:
                    click.echo(Texts.NO_WEB_BROWSER_ERROR_MSG)

            if port and port != proxy.tunnel_port:
                click.echo(Texts.CANNOT_USE_PORT.format(
                    required_port=port,
                    random_port=proxy.tunnel_port
                ))

            proxy_spinner.hide()
            click.echo(Texts.GO_TO_MSG.format(url=url))
            click.echo(Texts.PROXY_CREATED_MSG)
            wait_for_ctrl_c()
    except K8sProxyCloseError:
        err_message = Texts.PROXY_CLOSE_ERROR_MSG.format(app_name=k8s_app_name)
        raise ProxyClosingError(err_message)
    except LocalPortOccupiedError as exe:
        err_message = Texts.PROXY_CREATED_EXTENDED_ERROR_MSG.format(app_name=k8s_app_name, reason=exe.message)
        raise LaunchError(err_message)
    except K8sProxyOpenError:
        error_msg = Texts.PROXY_CREATED_ERROR_MSG.format(app_name=k8s_app_name)
        logger.exception(error_msg)
        raise LaunchError(error_msg)
    except LaunchError as e:
        raise e
    except Exception:
        err_message = Texts.WEB_APP_LAUCH_FAIL_MSG
        logger.exception(err_message)
        raise LaunchError(err_message)
