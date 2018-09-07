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

from collections import defaultdict
from sys import exit

from tabulate import tabulate
import click

from commands.experiment.common import EXPERIMENTS_LIST_HEADERS
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_pods
from util.logger import initialize_logger
import platform_resources.runs as runs_api
from util.system import handle_error
from cli_text_consts import EXPERIMENT_VIEW_CMD_TEXTS as TEXTS


logger = initialize_logger(__name__)


def container_status_to_msg(state) -> str:
    if not state:
        return TEXTS["container_not_created_msg"]
    if state.running is not None:
        return TEXTS["container_running_msg"] + str(state.running)
    if state.terminated is not None:
        return TEXTS["container_terminated_msg"] + str(state.terminated.reason)
    if state.waiting is not None:
        return TEXTS["container_waiting_msg"] + str(state.waiting)


def container_volume_mounts_to_msg(volume_mounts, spaces=7) -> str:
    indent = ' ' * spaces
    return indent.join([f'{mount.name} @ {mount.mount_path}\n' for mount in volume_mounts]) if volume_mounts else ''


def container_resources_to_msg(resources, spaces=9) -> str:
    msg = ''
    header_indent = ' ' * (spaces - 4)
    indent = ' ' * spaces
    if resources.requests:
        msg += header_indent
        msg += TEXTS["container_requests_list_header"].format(indent)
        msg += indent.join([f'{request_name}: {request_value}\n' for request_name, request_value
                            in resources.requests.items()])
    if resources.limits:
        msg += header_indent
        msg += TEXTS["container_limits_list_header"].format(indent)
        msg += indent.join([f'{limit_name}: {limit_value}\n' for limit_name, limit_value
                            in resources.limits.items()])

    return msg


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='v')
@click.argument("experiment_name")
@click.option('-tb', '--tensorboard', default=None, help=TEXTS["help_t"], is_flag=True)
@common_options()
@pass_state
def view(state: State, experiment_name: str, tensorboard: bool):
    """
    Displays details of an experiment.
    """
    try:
        namespace = get_kubectl_current_context_namespace()
        run = runs_api.get_run(name=experiment_name,
                               namespace=namespace)
        if not run:
            handle_error(user_msg=TEXTS["experiment_not_found_error_msg"].format(experiment_name=experiment_name))
            exit(2)

        click.echo(
            tabulate(
                [run.cli_representation],
                headers=EXPERIMENTS_LIST_HEADERS,
                tablefmt="orgtbl"))

        click.echo(TEXTS["pods_participating_list_header"])

        pods = get_pods(label_selector="runName=" + experiment_name)

        tabular_output = []

        for pod in pods:
            status_string = ""
            for cond in pod.status.conditions:
                msg = "" if not cond.reason else ", reason: " + cond.reason
                msg = msg + ",\nmessage: " + cond.message if cond.message else msg
                status_string = "     " + cond.type + ": " + cond.status + msg

            container_statuses = defaultdict(lambda: None)
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    container_statuses[container_status.name] = container_status.state

            container_details = []
            for container in pod.spec.containers:
                container_description = TEXTS["container_details_msg"].format(name=container.name,
                                                                              status=container_status_to_msg(
                                                                                  container_statuses[container.name]),
                                                                              volumes=container_volume_mounts_to_msg(
                                                                                  container.volume_mounts),
                                                                              resources=container_resources_to_msg(
                                                                                  container.resources))
                container_details.append(container_description)

            container_details = ''.join(container_details)
            tabular_output.append([
                pod.metadata.name, pod.metadata.uid, status_string,
                container_details
            ])
        click.echo(tabulate(tabular_output, TEXTS["pods_table_headers"], tablefmt="orgtbl"))

    except Exception:
        handle_error(logger, TEXTS["view_other_error_msg"], TEXTS["view_other_error_msg"])
        exit(1)
