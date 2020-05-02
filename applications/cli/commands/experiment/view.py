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

from collections import defaultdict
from sys import exit

from tabulate import tabulate
import click

from commands.experiment.common import EXPERIMENTS_LIST_HEADERS, wrap_text
from commands.launch.launch import tensorboard as tensorboard_command
from util.cli_state import common_options
from platform_resources.run import Run, RunKinds
from platform_resources.experiment import Experiment
from util.aliascmd import AliasCmd
from util.config import TBLT_TABLE_FORMAT
from util.k8s.k8s_info import get_kubectl_current_context_namespace, get_namespaced_pods, sum_mem_resources,\
    sum_cpu_resources, PodStatus, get_pod_events, add_bytes_to_unit
from util.k8s.k8s_statistics import get_highest_usage
from util.logger import initialize_logger
from util.system import handle_error, format_timestamp_for_cli
from cli_text_consts import ExperimentViewCmdTexts as Texts

logger = initialize_logger(__name__)

PREFIX_VALUES = {
    "E": 10**18,
    "P": 10**15,
    "T": 10**12,
    "G": 10**9,
    "M": 10**6,
    "K": 10**3
}
PREFIX_I_VALUES = {
    "Ei": 2**60,
    "Pi": 2**50,
    "Ti": 2**40,
    "Gi": 2**30,
    "Mi": 2**20,
    "Ki": 2**10
}

POD_CONDITIONS_MAX_WIDTH = 30
UID_MAX_WIDTH = 15
CONTAINER_DETAILS_MAX_WIDTH = 50


def container_status_to_msg(state) -> str:
    if not state:
        return Texts.CONTAINER_NOT_CREATED_MSG
    if state.running is not None:
        return Texts.CONTAINER_RUNNING_MSG + format_timestamp_for_cli(
            str(state.running.started_at))
    if state.terminated is not None:
        msg = Texts.CONTAINER_TERMINATED_MSG + str(state.terminated.reason)
        msg += Texts.REASON + wrap_text(str(state.terminated.message), width=CONTAINER_DETAILS_MAX_WIDTH) \
            if state.terminated.message else ''
        return msg
    if state.waiting is not None:
        return Texts.CONTAINER_WAITING_MSG + str(state.waiting.reason)

    raise ValueError(f'Container state: {state} not recognized.')


def container_volume_mounts_to_msg(volume_mounts, spaces=7) -> str:
    # convert read only bool flag to string
    ux_volume_mounts = []
    for vm in volume_mounts:
        rwro = "rw"
        if vm.read_only:
            rwro = "ro"
        ux_volume_mounts.append({
            "name": vm.name,
            "mount_path": vm.mount_path,
            "rwro": rwro
        })
    indent = ' ' * spaces
    return indent.join(
        [(wrap_text(
            f'{mount["name"]} <{mount["rwro"]}> @ {mount["mount_path"]}',
            width=CONTAINER_DETAILS_MAX_WIDTH,
            spaces=spaces + 2) + "\n")
         for mount in ux_volume_mounts]) if ux_volume_mounts else ''


def unify_units(name: str, value: str) -> str:
    if name == "cpu":
        if not value.endswith("m"):
            value_float = float(value) * 1000
            if value_float.is_integer():
                value = str(int(value_float)) + "m"
            else:
                value = str(value_float) + "m"
    elif name == "memory":
        value = add_bytes_to_unit(value)
    return f'{name}: {value}\n'


def container_resources_to_msg(resources, spaces=9) -> str:
    msg = ''
    header_indent = '\n' + ' ' * (spaces - 2)
    indent = ' ' * spaces
    if resources.requests:
        msg += header_indent
        msg += Texts.CONTAINER_REQUESTS_LIST_HEADER.format(indent)
        msg += indent.join([
            wrap_text(
                unify_units(request_name, request_value),
                width=CONTAINER_DETAILS_MAX_WIDTH,
                spaces=spaces + 2)
            for request_name, request_value in resources.requests.items()
        ])
    if resources.limits:
        msg += header_indent
        msg += Texts.CONTAINER_LIMITS_LIST_HEADER.format(indent)
        msg += indent.join([
            wrap_text(
                unify_units(limit_name, limit_value),
                width=CONTAINER_DETAILS_MAX_WIDTH,
                spaces=spaces + 2)
            for limit_name, limit_value in resources.limits.items()
        ])

    return msg


@click.command(
    help=Texts.HELP,
    short_help=Texts.SHORT_HELP,
    cls=AliasCmd,
    alias='v',
    options_metavar='[options]')
@click.argument("experiment_name")
@click.option(
    '-tb', '--tensorboard', default=None, help=Texts.HELP_T, is_flag=True)
@click.option('-u', '--username', help=Texts.HELP_U)
@common_options()
@click.pass_context
def view(ctx: click.Context, experiment_name: str, tensorboard: bool,
         username: str, accepted_run_kinds=(RunKinds.TRAINING.value, RunKinds.JUPYTER.value)):
    """
    Displays details of an experiment.
    """
    try:
        if username:
            namespace = username
        else:
            namespace = get_kubectl_current_context_namespace()

        run = Run.get(name=experiment_name, namespace=namespace)
        if not run or run.metadata.get('labels', {}).get('runKind') not in accepted_run_kinds:
            handle_error(
                user_msg=Texts.NOT_FOUND_ERROR_MSG.format(
                    experiment_name=experiment_name))
            exit(2)

        experiment = Experiment.get(name=experiment_name, namespace=namespace)
        if experiment:
            run.template_version = experiment.template_version

        click.echo(
            tabulate(
                [run.cli_representation],
                headers=EXPERIMENTS_LIST_HEADERS,
                tablefmt=TBLT_TABLE_FORMAT
            )
        )

        click.echo(Texts.PODS_PARTICIPATING_LIST_HEADER)

        pods = get_namespaced_pods(
            label_selector="runName=" + experiment_name, namespace=namespace)

        tabular_output = []
        containers_resources = []
        pending_pods = []

        for pod in pods:
            status_string = ""

            if pod.status.conditions:
                for cond in pod.status.conditions:
                    msg = "\n" if not cond.reason else "\n reason: " + \
                                                       wrap_text(cond.reason, width=POD_CONDITIONS_MAX_WIDTH)
                    msg = msg + ", \n message: " + wrap_text(cond.message, width=POD_CONDITIONS_MAX_WIDTH) \
                        if cond.message else msg
                    status_string += wrap_text(
                        cond.type + ": " + cond.status,
                        width=POD_CONDITIONS_MAX_WIDTH) + msg + "\n"
            else:
                pod_events = get_pod_events(
                    namespace=namespace, name=pod.metadata.name)

                for event in pod_events:
                    msg = "\n" if not event.reason else "\n reason: " + \
                                                        wrap_text(event.reason, width=POD_CONDITIONS_MAX_WIDTH)
                    msg = msg + ", \n message: " + wrap_text(event.message, width=POD_CONDITIONS_MAX_WIDTH) \
                        if event.message else msg
                    status_string += msg + "\n"

            if pod.status.phase.upper() == PodStatus.PENDING.value:
                pending_pods.append(pod.metadata.name)

            container_statuses = defaultdict(lambda: None)  # type: ignore
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    container_statuses[
                        container_status.name] = container_status.state

            container_details = []

            for container in pod.spec.containers:
                container_description = Texts.CONTAINER_DETAILS_MSG.format(
                    name=container.name,
                    status=container_status_to_msg(
                        container_statuses[container.name]),
                    volumes=container_volume_mounts_to_msg(
                        container.volume_mounts, spaces=2),
                    resources=container_resources_to_msg(
                        container.resources, spaces=4))
                container_details.append(container_description)
                containers_resources.append(container.resources)

            container_details_string = ''.join(container_details)

            tabular_output.append([
                pod.metadata.name,
                wrap_text(pod.metadata.uid, width=UID_MAX_WIDTH, spaces=0),
                status_string, container_details_string
            ])
        click.echo(
            tabulate(
                tabular_output, Texts.PODS_TABLE_HEADERS, tablefmt=TBLT_TABLE_FORMAT))

        try:
            cpu_requests_sum = sum_cpu_resources([
                container_resource.requests["cpu"]
                for container_resource in containers_resources
                if container_resource.requests
                and container_resource.requests.get("cpu")
            ])
            mem_requests_sum = sum_mem_resources([
                container_resource.requests["memory"]
                for container_resource in containers_resources
                if container_resource.requests
                and container_resource.requests.get("memory")
            ])
            cpu_limits_sum = sum_cpu_resources([
                container_resource.limits["cpu"]
                for container_resource in containers_resources
                if container_resource.limits
                and container_resource.limits.get("cpu")
            ])
            mem_limits_sum = sum_mem_resources([
                container_resource.limits["memory"]
                for container_resource in containers_resources
                if container_resource.limits
                and container_resource.limits.get("memory")
            ])
        except ValueError as exception:
            handle_error(
                logger,
                Texts.RESOURCES_SUM_PARSING_ERROR_MSG.format(
                    error_msg=str(exception)),
                Texts.RESOURCES_SUM_PARSING_ERROR_MSG.format(
                    error_msg=str(exception)))

        click.echo(Texts.RESOURCES_SUM_LIST_HEADER)
        click.echo(
            tabulate(
                list(
                    zip(Texts.RESOURCES_SUM_TABLE_ROWS_HEADERS, [
                        cpu_requests_sum, mem_requests_sum, cpu_limits_sum,
                        mem_limits_sum
                    ])),
                Texts.RESOURCES_SUM_TABLE_HEADERS,
                tablefmt=TBLT_TABLE_FORMAT))

        if tensorboard:
            click.echo()
            ctx.invoke(tensorboard_command, experiment_name=[experiment_name])

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

                if not cpu and not memory:
                    exit(0)

                if cpu and memory:
                    resources = "number of cpus and amount of memory"
                elif cpu:
                    resources = "number of cpus"
                else:
                    resources = "amount of memory"

                click.echo(
                    Texts.INSUFFICIENT_RESOURCES_MESSAGE.format(
                        resources=resources))
                click.echo()
                top_cpu_users, top_mem_users = get_highest_usage()
                click.echo(
                    Texts.TOP_CPU_CONSUMERS.format(consumers=", ".join(res.user_name
                        for res in top_cpu_users[0:3 if len(top_cpu_users) > 2
                                                 else len(top_cpu_users)])))
                click.echo(
                    Texts.TOP_MEMORY_CONSUMERS.format(consumers=", ".join(res.user_name
                        for res in top_mem_users[0:3 if len(top_mem_users) > 2
                                                 else len(top_mem_users)])))
            except Exception:
                click.echo(Texts.PROBLEMS_WHILE_GATHERING_USAGE_DATA)
                logger.exception(
                    Texts.PROBLEMS_WHILE_GATHERING_USAGE_DATA_LOGS)

    except Exception:
        handle_error(logger, Texts.VIEW_OTHER_ERROR_MSG.format(name=experiment_name),
                     Texts.VIEW_OTHER_ERROR_MSG.format(name=experiment_name))
        exit(1)
