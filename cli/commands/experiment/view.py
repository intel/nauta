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

import sys

from tabulate import tabulate
import click

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_pods
from util.logger import initialize_logger
import platform_resources.runs as runs_api


logger = initialize_logger(__name__)

HELP = "Displays details of experiment with a given name."
HELP_T = "If given, then exposes a tensorboard's instance with experiment's data."

CONTAINER_DETAILS = '''
- Name: {name}
   - Status: {status}
   - Volumes:
       {volumes}
   - Resources:
{resources}
'''


def container_status_to_msg(state) -> str:
    if state.running is not None:
        return "Running, " + str(state.running)
    if state.terminated is not None:
        return "Terminated, " + str(state.terminated.reason)
    if state.waiting is not None:
        return "Waiting, " + str(state.waiting)


def container_volume_mounts_to_msg(volume_mounts, spaces=7) -> str:
    indent = ' ' * spaces
    return indent.join([f'{mount.name} @ {mount.mount_path}\n' for mount in volume_mounts]) if volume_mounts else ''


def container_resources_to_msg(resources, spaces=9) -> str:
    msg = ''
    header_indent = ' ' * (spaces - 4)
    indent = ' ' * spaces
    if resources.requests:
        msg += header_indent
        msg += '- Requests:\n{}'.format(indent)
        msg += indent.join([f'{request_name}: {request_value}\n' for request_name, request_value
                            in resources.requests.items()])
    if resources.limits:
        msg += header_indent
        msg += '- Limits:\n{}'.format(indent)
        msg += indent.join([f'{limit_name}: {limit_value}\n' for limit_name, limit_value
                            in resources.limits.items()])

    return msg


@click.command(short_help=HELP, cls=AliasCmd, alias='v')
@click.argument("experiment_name")
@click.option('-tb', '--tensorboard', default=None, help=HELP_T, is_flag=True)
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
            click.echo(f"Experiment \"{experiment_name}\" not found.")
            sys.exit(2)

        click.echo(
            tabulate(
                [run.cli_representation],
                headers=[
                    "Name", "Parameters", "Metrics", "Submission date",
                    "Submitter", "Status", "Template name"
                ],
                tablefmt="orgtbl"))

        click.echo("\nPods participating in the execution:\n")

        pods = get_pods(label_selector="runName=" + experiment_name)

        tabular_output = []

        for pod in pods:
            status_string = ""
            for cond in pod.status.conditions:
                msg = "" if not cond.reason else ", reason: " + cond.reason
                status_string = "     " + cond.type + ": " + cond.status + msg

            container_statuses = {}
            for container_status in pod.status.container_statuses:
                container_statuses[container_status.name] = container_status.state

            container_details = []
            for container in pod.spec.containers:
                container_description = CONTAINER_DETAILS.format(name=container.name,
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
        if pods:
            click.echo(
                tabulate(
                    tabular_output,
                    headers=['Name', 'Uid', 'Status', 'Container Details'],
                    tablefmt="orgtbl"))
        else:
            click.echo('At this moment there are no pods connected with this experiment.')

    except Exception:
        error_msg = 'Failed to get experiment.'
        logger.exception(error_msg)
        click.echo(error_msg)
        sys.exit(1)
