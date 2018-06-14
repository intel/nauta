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
from kubernetes import client, config

from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.logger import initialize_logger
import platform_resources.runs as runs_api


HELP = "Displays details of experiment with a given name."
HELP_T = "If given - exposes a tensorboard's instance with experiment's data."

logger = initialize_logger(__name__)


def container_status_to_msg(state):
    if state.running is not None:
        return "Running, " + str(state.running)
    if state.terminated is not None:
        return "Terminated, " + str(state.terminated.reason)
    if state.waiting is not None:
        return "Waiting, " + str(state.waiting)


def container_volume_mounts_to_msg(volume_mounts):
    ret = "\n"
    for mount in volume_mounts:
        ret += "       " + mount.name + " @ " + mount.mount_path + "\n"
    return ret[:-1]


def container_resources_to_msg(resources):
    ret = "\n"
    if resources.requests is not None:
        ret += "    - Requests:\n"
        for k, v in resources.requests.items():
            ret += "       " + k + ": " + str(v) + "\n"
    if resources.limits is not None:
        ret = ret[:-1] + "\n    - Limits:\n"
        for k, v in resources.limits.items():
            ret += "      " + k + ": " + str(v) + "\n"
    return ret[:-1]


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
        runs = runs_api.list_runs(name_filter=experiment_name,
                                  namespace=namespace)

        if not runs:
            click.echo(f"Experiment \"{experiment_name}\" not found.")
            sys.exit(2)

        run = runs[0]
        click.echo(
            tabulate(
                [run.cli_representation],
                headers=[
                    "Name", "Parameters", "Metrics", "Submission date",
                    "Submitter", "Status", "Template name"
                ],
                tablefmt="orgtbl"))

        click.echo("\nPods participating in the execution:\n")

        config.load_kube_config()
        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(
            watch=False, label_selector="runName=" + experiment_name)
        containers_details = {}
        tabular_output = []
        for i in ret.items:
            status_string = ""
            for cond in i.status.conditions:
                msg = "" if cond.reason is None else ", reason: " + cond.reason
                status_string = "     " + cond.type + ": " + cond.status + msg
            for container in i.spec.containers:
                containers_details[container.name] = {
                    "container_spec": container,
                    "status": None
                }
            for st in i.status.container_statuses:
                containers_details[st.name]["status"] = st
            container_details = ""
            for c_k, c_v in containers_details.items():
                container_details += f"- Name: {c_k}\n   - Status: " + container_status_to_msg(
                    c_v["status"].state
                ) + "\n   - Volumes: " + container_volume_mounts_to_msg(
                    c_v["container_spec"].volume_mounts
                ) + "\n   - Resources: " + container_resources_to_msg(
                    c_v["container_spec"].resources) + "\n\n"
            tabular_output.append([
                i.metadata.name, i.metadata.uid, status_string,
                container_details
            ])
        if ret.items:
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
