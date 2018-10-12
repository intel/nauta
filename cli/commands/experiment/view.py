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
from commands.launch.launch import tensorboard as tensorboard_command
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_namespaced_pods, sum_mem_resources,\
    sum_cpu_resources, PodStatus, get_pod_events, add_bytes_to_unit
from util.k8s.k8s_statistics import get_highest_usage
from util.logger import initialize_logger
import platform_resources.runs as runs_api
from util.system import handle_error
from cli_text_consts import ExperimentViewCmdTexts as Texts


logger = initialize_logger(__name__)

PREFIX_VALUES = {"E": 10 ** 18, "P": 10 ** 15, "T": 10 ** 12, "G": 10 ** 9, "M": 10 ** 6, "K": 10 ** 3}
PREFIX_I_VALUES = {"Ei": 2 ** 60, "Pi": 2 ** 50, "Ti": 2 ** 40, "Gi": 2 ** 30, "Mi": 2 ** 20, "Ki": 2 ** 10}


def container_status_to_msg(state) -> str:
    if not state:
        return Texts.CONTAINER_NOT_CREATED_MSG
    if state.running is not None:
        return Texts.CONTAINER_RUNNING_MSG + str(state.running)
    if state.terminated is not None:
        return Texts.CONTAINER_TERMINATED_MSG + str(state.terminated.reason)
    if state.waiting is not None:
        return Texts.CONTAINER_WAITING_MSG + str(state.waiting)


def container_volume_mounts_to_msg(volume_mounts, spaces=7) -> str:
    indent = ' ' * spaces
    return indent.join([f'{mount.name} @ {mount.mount_path}\n' for mount in volume_mounts]) if volume_mounts else ''


def unify_units(name: str, value: str) -> str:
    if name == "cpu":
        if not value.endswith("m"):
            value = float(value) * 1000
            if value.is_integer():
                value = str(int(value)) + "m"
            else:
                value = str(value) + "m"
    elif name == "mem":
        value = add_bytes_to_unit(value)
    return f'{name}: {value}\n'


def container_resources_to_msg(resources, spaces=9) -> str:
    msg = ''
    header_indent = ' ' * (spaces - 4)
    indent = ' ' * spaces
    if resources.requests:
        msg += header_indent
        msg += Texts.CONTAINER_REQUESTS_LIST_HEADER.format(indent)
        msg += indent.join([unify_units(request_name, request_value) for request_name, request_value
                            in resources.requests.items()])
    if resources.limits:
        msg += header_indent
        msg += Texts.CONTAINER_LIMITS_LIST_HEADER.format(indent)
        msg += indent.join([unify_units(limit_name, limit_value) for limit_name, limit_value
                            in resources.limits.items()])

    return msg


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='v')
@click.argument("experiment_name")
@click.option('-tb', '--tensorboard', default=None, help=Texts.HELP_T, is_flag=True)
@click.option('-u', '--username', help=Texts.HELP_U)
@common_options()
@pass_state
@click.pass_context
def view(context, state: State, experiment_name: str, tensorboard: bool, username: str):
    """
    Displays details of an experiment.
    """
    try:
        if username:
            namespace = username
        else:
            namespace = get_kubectl_current_context_namespace()

        run = runs_api.get_run(name=experiment_name,
                               namespace=namespace)
        if not run:
            handle_error(user_msg=Texts.EXPERIMENT_NOT_FOUND_ERROR_MSG.format(experiment_name=experiment_name))
            exit(2)

        click.echo(
            tabulate(
                [run.cli_representation],
                headers=EXPERIMENTS_LIST_HEADERS,
                tablefmt="orgtbl"))

        click.echo(Texts.PODS_PARTICIPATING_LIST_HEADER)

        pods = get_namespaced_pods(label_selector="runName=" + experiment_name, namespace=namespace)

        tabular_output = []
        containers_resources = []
        pending_pods = []

        for pod in pods:
            status_string = ""
            for cond in pod.status.conditions:
                msg = "\n" if not cond.reason else "\n reason: " + cond.reason
                msg = msg + ", \n message: " + cond.message if cond.message else msg
                status_string += cond.type + ": " + cond.status + msg

            if pod.status.phase.upper() == PodStatus.PENDING.value:
                pending_pods.append(pod.metadata.name)

            container_statuses = defaultdict(lambda: None)
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    container_statuses[container_status.name] = container_status.state

            container_details = []

            for container in pod.spec.containers:
                container_description = Texts.CONTAINER_DETAILS_MSG.format(name=container.name,
                                                                           status=container_status_to_msg(
                                                                               container_statuses[container.name]),
                                                                           volumes=container_volume_mounts_to_msg(
                                                                               container.volume_mounts,
                                                                               spaces=2),
                                                                           resources=container_resources_to_msg(
                                                                               container.resources, spaces=4))
                container_details.append(container_description)
                containers_resources.append(container.resources)

            container_details = ''.join(container_details)

            uid = pod.metadata.uid.replace("-", "-\n")
            tabular_output.append([
                pod.metadata.name, uid, status_string,
                container_details
            ])
        click.echo(tabulate(tabular_output, Texts.PODS_TABLE_HEADERS, tablefmt="orgtbl"))

        try:
            cpu_requests_sum = sum_cpu_resources(
                [container_resource.requests["cpu"]
                 for container_resource in containers_resources if container_resource.requests and
                 container_resource.requests.get("cpu")])
            mem_requests_sum = sum_mem_resources(
                [container_resource.requests["memory"]
                 for container_resource in containers_resources if container_resource.requests and
                 container_resource.requests.get("memory")])
            cpu_limits_sum = sum_cpu_resources(
                [container_resource.limits["cpu"]
                 for container_resource in containers_resources if container_resource.limits and
                 container_resource.limits.get("cpu")])
            mem_limits_sum = sum_mem_resources(
                [container_resource.limits["memory"]
                 for container_resource in containers_resources if container_resource.limits and
                 container_resource.limits.get("memory")])
        except ValueError as exception:
            handle_error(logger, Texts.RESOURCES_SUM_PARSING_ERROR_MSG.format(error_msg=str(exception)),
                         Texts.RESOURCES_SUM_PARSING_ERROR_MSG.format(error_msg=str(exception)))

        click.echo(Texts.RESOURCES_SUM_LIST_HEADER)
        click.echo(
            tabulate(
                list(
                    zip(
                        Texts.RESOURCES_SUM_TABLE_ROWS_HEADERS,
                        [cpu_requests_sum, mem_requests_sum, cpu_limits_sum, mem_limits_sum]
                    )
                ),
                Texts.RESOURCES_SUM_TABLE_HEADERS, tablefmt="orgtbl")
        )

        if tensorboard:
            click.echo()
            context.invoke(tensorboard_command, experiment_name=[experiment_name])

        if pending_pods:
            click.echo()
            try:
                cpu = False
                memory = False
                for pod in pending_pods:
                    events_list = get_pod_events(namespace=namespace, name=pod)
                    for event in events_list:
                        if "insufficient cpu" in event.message.lower():
                            cpu = True
                        elif "insufficient memory" in event.message.lower():
                            memory = True
                        if cpu and memory:
                            break
                    if cpu and memory:
                        break

                if cpu and memory:
                    resources = "number of cpus and amount of memory"
                elif cpu:
                    resources = "number of cpus"
                else:
                    resources = "amount of memory"

                click.echo(Texts.INSUFFICIENT_RESOURCES_MESSAGE.format(resources=resources))
                click.echo()
                top_cpu_users, top_mem_users = get_highest_usage()
                click.echo(Texts.TOP_CPU_CONSUMERS.format(consumers=", ".join(
                    [res.user_name for res in top_cpu_users[0:3 if len(top_cpu_users) > 2 else len(top_cpu_users)]])))
                click.echo(Texts.TOP_MEMORY_CONSUMERS.format(consumers=", ".join(
                    [res.user_name for res in top_mem_users[0:3 if len(top_mem_users) > 2 else len(top_mem_users)]])))
            except Exception:
                click.echo(Texts.PROBLEMS_WHILE_GATHERING_USAGE_DATA)
                logger.exception(Texts.PROBLEMS_WHILE_GATHERING_USAGE_DATA_LOGS)

    except Exception:
        handle_error(logger, Texts.VIEW_OTHER_ERROR_MSG, Texts.VIEW_OTHER_ERROR_MSG)
        exit(1)
