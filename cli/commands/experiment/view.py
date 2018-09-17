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
from typing import List
from sys import exit

from tabulate import tabulate
import click

from commands.experiment.common import EXPERIMENTS_LIST_HEADERS
from commands.launch.launch import tensorboard as tensorboard_command
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


def sum_cpu_resources(cpu_resources: List[str]):
    """ Sum cpu resources given in k8s format and return the sum in the same format. """
    cpu_sum = 0
    for cpu_resource in cpu_resources:
        if not cpu_resource:
            continue
        # If CPU resources are gives as for example 100m, we simply strip last character and sum leftover numbers.
        elif cpu_resource[-1] == "m":
            cpu_sum += int(cpu_resource[:-1])
        # Else we assume that cpu resources are given as float value of normal CPUs instead of miliCPUs.
        else:
            cpu_sum += int(float(cpu_resource) * 1000)
    return str(cpu_sum) + "m"


def sum_mem_resources(mem_resources: List[str]):
    """
    Sum memory resources given in k8s format and return the sum converted to byte units with base 2 - for example KiB.
    """
    PREFIX_VALUES = {"E": 10 ** 18, "P": 10 ** 15, "T": 10 ** 12, "G": 10 ** 9, "M": 10 ** 6, "K": 10 ** 3}
    PREFIX_I_VALUES = {"Ei": 2 ** 60, "Pi": 2 ** 50, "Ti": 2 ** 40, "Gi": 2 ** 30, "Mi": 2 ** 20, "Ki": 2 ** 10}
    mem_sum = 0

    for mem_resource in mem_resources:
        if not mem_resource:
            continue
        # If last character is "i" then assume that resource is given as for example 1000Ki.
        elif mem_resource[-1] == "i" and mem_resource[-2:] in PREFIX_I_VALUES:
            prefix = mem_resource[-2:]
            mem_sum += int(mem_resource[:-2]) * PREFIX_I_VALUES[prefix]
        # If last character is one of the normal exponent prefixes (with base 10) then assume that resource is given
        # as for example 1000K.
        elif mem_resource[-1] in PREFIX_VALUES:
            prefix = mem_resource[-1]
            mem_sum += int(mem_resource[:-1]) * PREFIX_VALUES[prefix]
        # If there is e contained inside resource string then assume that it is given in exponential format.
        elif "e" in mem_resource:
            mem_sum += int(float(mem_resource))
        else:
            mem_sum += int(mem_resource)

    mem_sum_partial_strs = []
    for prefix, value in PREFIX_I_VALUES.items():
        mem_sum_partial = mem_sum // value
        if mem_sum_partial != 0:
            mem_sum_partial_strs.append(str(mem_sum_partial) + prefix + "B")
            mem_sum = mem_sum % value
    if len(mem_sum_partial_strs) == 0:
        return "0KiB"
    else:
        return " ".join(mem_sum_partial_strs)


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='v')
@click.argument("experiment_name")
@click.option('-tb', '--tensorboard', default=None, help=TEXTS["help_t"], is_flag=True)
@common_options()
@pass_state
@click.pass_context
def view(context, state: State, experiment_name: str, tensorboard: bool):
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
        containers_resources = []

        for pod in pods:
            status_string = ""
            for cond in pod.status.conditions:
                msg = "\n" if not cond.reason else ", reason: " + cond.reason + "\n"
                msg = msg + ", message: " + cond.message if cond.message else msg
                status_string += cond.type + ": " + cond.status + msg

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
                containers_resources.append(container.resources)

            container_details = ''.join(container_details)
            tabular_output.append([
                pod.metadata.name, pod.metadata.uid, status_string,
                container_details
            ])
        click.echo(tabulate(tabular_output, TEXTS["pods_table_headers"], tablefmt="orgtbl"))

        try:
            cpu_requests_sum = sum_cpu_resources(
                [container_resource.requests["cpu"]
                 for container_resource in containers_resources if container_resource.requests])
            mem_requests_sum = sum_mem_resources(
                [container_resource.requests["memory"]
                 for container_resource in containers_resources if container_resource.requests])
            cpu_limits_sum = sum_cpu_resources(
                [container_resource.limits["cpu"]
                 for container_resource in containers_resources if container_resource.limits])
            mem_limits_sum = sum_mem_resources(
                [container_resource.limits["memory"]
                 for container_resource in containers_resources if container_resource.limits])
        except ValueError as exception:
            handle_error(logger, TEXTS["resources_sum_parsing_error_msg"].format(error_msg=str(exception)),
                         TEXTS["resources_sum_parsing_error_msg"].format(error_msg=str(exception)))

        click.echo(TEXTS["resources_sum_list_header"])
        click.echo(
            tabulate(
                list(
                    zip(
                        TEXTS["resources_sum_table_rows_headers"],
                        [cpu_requests_sum, mem_requests_sum, cpu_limits_sum, mem_limits_sum]
                    )
                ),
                TEXTS["resources_sum_table_headers"], tablefmt="orgtbl")
        )

        if tensorboard:
            click.echo()
            context.invoke(tensorboard_command, experiment_name=[experiment_name])

    except Exception:
        handle_error(logger, TEXTS["view_other_error_msg"], TEXTS["view_other_error_msg"])
        exit(1)
