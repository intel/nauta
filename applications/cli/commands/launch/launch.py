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

import sys
from time import sleep
from typing import Optional, List
from http import HTTPStatus

import click

from util.cli_state import common_options
from tensorboard.client import TensorboardServiceClient, TensorboardStatus, build_tensorboard_run_list
from util.spinner import spinner
from util.aliascmd import AliasCmd, AliasGroup
from util.app_names import NAUTAAppNames
from util.exceptions import LaunchError, ProxyClosingError
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.launcher import launch_app
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import LaunchCmdTexts as Texts


logger = initialize_logger('commands.launch')

FORWARDED_URL = 'http://localhost:{}'

TENSORBOARD_TRIES_COUNT = 60
TENSORBOARD_CHECK_BACKOFF_SECONDS = 5


# noinspection PyUnusedLocal
@click.command(cls=AliasCmd, alias='ui', short_help=Texts.WEBUI_HELP, help=Texts.WEBUI_HELP,
               options_metavar='[options]')
@common_options()
@click.pass_context
@click.option('-n', '--no-launch', is_flag=True, help=Texts.HELP_N)
@click.option('-pn', '--port-number', type=click.IntRange(1024, 65535), help=Texts.HELP_P)
def webui(ctx: click.Context, no_launch: bool, port_number: int):
    """ Subcommand for launching webUI with credentials """
    launch_app_with_proxy(NAUTAAppNames.INGRESS, no_launch, port_number)


# noinspection PyUnusedLocal
@click.command(cls=AliasCmd, alias='tb', help=Texts.TB_HELP, short_help=Texts.SHORT_TB_HELP,
               options_metavar='[options]')
@common_options(admin_command=False)
@click.pass_context
@click.option('-n', '--no-launch', is_flag=True, help=Texts.HELP_N)
@click.option('-tscp', '--tensorboard-service-client-port', type=click.IntRange(1024, 65535),
              help=Texts.TB_HELP_TSCP)
@click.option('-pn', '--port-number', type=click.IntRange(1024, 65535), help=Texts.HELP_P)
@click.argument("experiment-name", type=str, required=True, nargs=-1)
def tensorboard(ctx: click.Context, no_launch: bool, tensorboard_service_client_port: Optional[int],
                port_number: Optional[int], experiment_name: List[str]):
    """ Subcommand for launching tensorboard with credentials """
    current_namespace = get_kubectl_current_context_namespace()

    with spinner(Texts.TB_WAITING_MSG) as proxy_spinner, \
            K8sProxy(nauta_app_name=NAUTAAppNames.TENSORBOARD_SERVICE, app_name='tensorboard-service',
                     namespace=current_namespace, port=tensorboard_service_client_port) as proxy:

        tensorboard_service_client = TensorboardServiceClient(address=f'http://127.0.0.1:{proxy.tunnel_port}')

        requested_runs = build_tensorboard_run_list(exp_list=experiment_name, current_namespace=current_namespace)

        # noinspection PyBroadException
        try:
            tb = tensorboard_service_client.create_tensorboard(requested_runs)
            if tb.invalid_runs:
                list_of_invalid_runs = ', '.join(f'{item.get("owner")}/{item.get("name")}'
                                                  for item in tb.invalid_runs)
                click.echo(Texts.TB_INVALID_RUNS_MSG.format(invalid_runs=list_of_invalid_runs))
        except Exception as exe:
            err_message = Texts.TB_CREATE_ERROR_MSG
            if hasattr(exe, 'error_code') and exe.error_code == HTTPStatus.UNPROCESSABLE_ENTITY:  # type: ignore
                err_message = str(exe)
            handle_error(logger, err_message, err_message, add_verbosity_msg=ctx.obj.verbosity == 0)
            sys.exit(1)

        for i in range(TENSORBOARD_TRIES_COUNT):
            # noinspection PyTypeChecker
            # tb.id is str
            tb = tensorboard_service_client.get_tensorboard(tb.id)
            if not tb:
                sleep(TENSORBOARD_CHECK_BACKOFF_SECONDS)
                continue
            if tb.status == TensorboardStatus.RUNNING:
                proxy_spinner.hide()
                launch_app_with_proxy(k8s_app_name=NAUTAAppNames.TENSORBOARD, no_launch=no_launch,
                                      namespace=current_namespace, port=port_number,
                                      app_name=f"tensorboard-{tb.id}")
                return
            logger.warning(Texts.TB_WAITING_FOR_TB_MSG.format(tb_id=tb.id, tb_status_value=tb.status.value))
            sleep(TENSORBOARD_CHECK_BACKOFF_SECONDS)

        click.echo(Texts.TB_TIMEOUT_ERROR_MSG)
        sys.exit(2)


@click.group(short_help=Texts.HELP, help=Texts.HELP, cls=AliasGroup, alias='l',
             subcommand_metavar="COMMAND [options] [args]...")
def launch():
    pass


def launch_app_with_proxy(k8s_app_name: NAUTAAppNames, no_launch: bool, port: int = None, namespace: str = None,
                          app_name: str = None):
    # noinspection PyBroadException
    try:
        launch_app(k8s_app_name=k8s_app_name, no_launch=no_launch, port=port, namespace=namespace, app_name=app_name)
    except LaunchError as exe:
        handle_error(logger, exe.message, exe.message)
        exit(1)
    except ProxyClosingError:
        handle_error(user_msg=Texts.APP_PROXY_EXISTS_ERROR_MSG)
    except Exception:
        handle_error(logger, Texts.APP_PROXY_OTHER_ERROR_MSG, Texts.APP_PROXY_OTHER_ERROR_MSG)
        exit(1)


launch.add_command(webui)
launch.add_command(tensorboard)
