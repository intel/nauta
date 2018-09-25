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
import re
import sys
from sys import exit
from enum import Enum


import click
from typing import List, Tuple

from commands.experiment.common import RunKinds
import util.k8s.kubectl as kubectl
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_current_namespace
from platform_resources.run_model import Run, RunStatus
from platform_resources.runs import list_runs, update_run
from platform_resources.experiment_model import ExperimentStatus
from platform_resources.experiments import update_experiment, get_experiment
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from util.app_names import DLS4EAppNames
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.helm import delete_helm_release
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.k8s import pods as k8s_pods
from util.logger import initialize_logger
from util.system import handle_error
from cli_text_consts import EXPERIMENT_CANCEL_CMD_TEXTS as TEXTS
from util.k8s.k8s_info import PodStatus


logger = initialize_logger(__name__)

experiment_name = 'experiment'
experiment_name_plural = 'experiments'


@click.command(help=TEXTS["help"], short_help=TEXTS["help"], cls=AliasCmd, alias='c')
@click.argument("name", required=False)
@click.option('-m', '--match', help=TEXTS["help_m"])
@click.option('-p', '--purge', help=TEXTS["help_p"], is_flag=True)
@click.option('-i', '--pod-ids', help=TEXTS["help_i"])
@click.option('-s', '--pod-status', help=TEXTS["help_s"].format(available_statuses=PodStatus.all_members()))
@common_options()
@pass_state
def cancel(state: State, name: str, match: str, purge: bool, pod_ids: str, pod_status: str,
           listed_runs_kinds: List[Enum] = [RunKinds.TRAINING, RunKinds.JUPYTER]):
    """
    Cancels chosen experiments based on a name provided as a parameter.
    """

    # check whether we have runs with a given name

    if name and match:
        handle_error(user_msg=TEXTS["name_m_both_given_error_msg"])
        exit(1)

    if not name and not match and not (pod_ids or pod_status):
        handle_error(user_msg=TEXTS["name_m_none_given_error_msg"])
        exit(1)

    current_namespace = get_current_namespace()

    if pod_ids or pod_status:
        if not name:
            name = match

        cancel_pods_mode(namespace=current_namespace, run_name=name, pod_ids=pod_ids, pod_status=pod_status)
        exit(0)

    search_for_experiment = False

    if name:
        exp_to_be_cancelled = get_experiment(namespace=current_namespace, name=name)

        if exp_to_be_cancelled:
            search_for_experiment = True
        else:
            name = f"^{name}$"
    else:
        name = match

    list_of_all_runs = None

    list_of_applicable_states = [RunStatus.QUEUED, RunStatus.RUNNING]

    if purge:
        list_of_applicable_states.extend([RunStatus.FAILED, RunStatus.COMPLETE, RunStatus.CANCELLED])

    try:
        if search_for_experiment:
            list_of_all_runs = list_runs(namespace=current_namespace, exp_name_filter=name,
                                         state_list=list_of_applicable_states, run_kinds_filter=listed_runs_kinds)
        else:
            list_of_all_runs = list_runs(namespace=current_namespace, name_filter=name,
                                         state_list=list_of_applicable_states, run_kinds_filter=listed_runs_kinds)
    except Exception:
        handle_error(logger, TEXTS["list_runs_error_msg"].format(experiment_name_plural=experiment_name_plural),
                     TEXTS["list_runs_error_msg"].format(experiment_name_plural=experiment_name_plural))
        exit(1)

    if not list_of_all_runs:
        handle_error(
            user_msg=TEXTS["lack_of_experiments_error_msg"].format(experiment_name_plural=experiment_name_plural,
                                                                   experiment_name=experiment_name)
        )
        exit(1)

    # check whether we have at least one experiment in state other than CANCELLED
    list_of_runs_to_be_deleted = []
    names_of_cancelled_runs = []

    if not purge:
        # check whether we have at least one experiment in state other than CANCELLED
        for run in list_of_all_runs:
            if run.state != RunStatus.CANCELLED:
                list_of_runs_to_be_deleted.append(run)
            else:
                names_of_cancelled_runs.append(run.name)

        if not list_of_runs_to_be_deleted:
            handle_error(
                user_msg=TEXTS["experiments_already_cancelled_error_msg"].format(
                    experiment_name_plural=experiment_name_plural
                )
            )
            exit(1)
        elif len(list_of_runs_to_be_deleted) != len(list_of_all_runs):
            click.echo(TEXTS["already_cancelled_list_header"].format(experiment_name_plural=experiment_name_plural))
            for name in names_of_cancelled_runs:
                click.echo(f"     - {name}")
            click.echo(TEXTS["can_be_cancelled_list_header"].format(experiment_name_plural=experiment_name_plural))
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
        else:
            click.echo(TEXTS["will_be_cancelled_list_header"].format(experiment_name_plural=experiment_name_plural))
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
    else:
        list_of_runs_to_be_deleted = list_of_all_runs
        click.echo(TEXTS["will_be_purged_list_header"].format(experiment_name_plural=experiment_name_plural))
        for name in list_of_runs_to_be_deleted:
            click.echo(f"     - {name.name}")

    if not click.confirm(TEXTS["confirm_cancel_msg"].format(experiment_name_plural=experiment_name_plural)):
        handle_error(
            user_msg=TEXTS["cancellation_aborted_msg"].format(
                experiment_name_plural=experiment_name_plural
            )
        )
        exit(2)

    # group runs by experiments
    exp_with_runs = defaultdict(list)

    for run in list_of_runs_to_be_deleted:
        exp_with_runs[run.experiment_name].append(run)

    deleted_runs = []
    not_deleted_runs = []

    if purge:
        # Connect to elasticsearch in order to purge run logs
        try:
            with K8sProxy(DLS4EAppNames.ELASTICSEARCH) as proxy:
                es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                                   verify_certs=False, use_ssl=False)
                for exp_name, run_list in exp_with_runs.items():
                    try:
                        exp_del_runs, exp_not_del_runs = purge_experiment(exp_name=exp_name,
                                                                          runs_to_purge=run_list,
                                                                          namespace=current_namespace,
                                                                          k8s_es_client=es_client)
                        deleted_runs.extend(exp_del_runs)
                        not_deleted_runs.extend(exp_not_del_runs)
                    except Exception:
                        handle_error(logger, TEXTS["other_cancelling_error_msg"])
                        not_deleted_runs.extend(run_list)
        except K8sProxyCloseError:
            handle_error(logger, TEXTS["proxy_closing_error_log_msg"], TEXTS["proxy_closing_error_user_msg"])
            exit(1)
        except LocalPortOccupiedError as exe:
            handle_error(logger, TEXTS["port_occupied_error_log_msg"],
                         TEXTS["port_occupied_error_user_msg"].format(exception_message=exe.message))
            exit(1)
        except K8sProxyOpenError:
            handle_error(logger, TEXTS["proxy_open_error_msg"], TEXTS["proxy_open_error_msg"])
            exit(1)
    else:
        for exp_name, run_list in exp_with_runs.items():
            try:
                exp_del_runs, exp_not_del_runs = cancel_experiment(exp_name=exp_name, runs_to_cancel=run_list,
                                                                   namespace=current_namespace)
                deleted_runs.extend(exp_del_runs)
                not_deleted_runs.extend(exp_not_del_runs)
            except Exception:
                handle_error(logger, TEXTS["other_cancelling_error_msg"])
                not_deleted_runs.extend(run_list)

    if deleted_runs:
        click.echo(TEXTS["successfully_cancelled_list_header"].format(experiment_name_plural=experiment_name_plural))
        for run in deleted_runs:
            click.echo(f"     - {run.name}")

    if not_deleted_runs:
        click.echo(TEXTS["failed_to_cancel_list_header"].format(experiment_name_plural=experiment_name_plural))
        for run in not_deleted_runs:
            click.echo(f"     - {run.name}")
        sys.exit(1)


def purge_experiment(exp_name: str, runs_to_purge: List[Run],
                     k8s_es_client: K8sElasticSearchClient,
                     namespace: str) -> Tuple[List[Run], List[Run]]:
    """
       Purge experiment with a given name by cancelling runs given as a parameter. If given experiment
       contains more runs than is in the list of runs - experiment's state remains intact.

       :param exp_name: name of an experiment to which belong runs passed in run_list parameter
       :param runs_to_purge: list of runs that should be purged, they have to belong to exp_name experiment
       :param k8s_es_client: Kubernetes ElasticSearch client
       :param namespace: namespace where experiment is located
       :return: two list - first contains runs that were cancelled successfully, second - those which weren't
       """
    logger.debug(f"Purging {exp_name} experiment ...")

    purged_runs = []
    not_purged_runs = []

    experiment = get_experiment(name=exp_name, namespace=namespace)
    if not experiment:
        raise RuntimeError(TEXTS["get_experiment_error_msg"])

    experiment_runs = list_runs(namespace=namespace, exp_name_filter=exp_name)
    # check whether experiment has more runs that should be cancelled
    cancel_whole_experiment = (len(experiment_runs) == len(runs_to_purge))
    if cancel_whole_experiment:
        experiment.state = ExperimentStatus.CANCELLING
        update_experiment(experiment, namespace)

    try:
        cancelled_runs, not_cancelled_runs = cancel_experiment_runs(runs_to_cancel=runs_to_purge, namespace=namespace)
        not_purged_runs = not_cancelled_runs
        for run in cancelled_runs:
            logger.debug(f"Purging {run.name} run ...")
            click.echo(TEXTS["purging_start_msg"].format(run_name=run.name))
            try:
                # purge helm release
                delete_helm_release(run.name, namespace=namespace, purge=True)
                # delete run
                kubectl.delete_k8s_object("run", run.name)
                purged_runs.append(run)
            except Exception as exe:
                not_purged_runs.append(run)
                logger.exception("Error during purging runs.")
                # occurence of NotFound error may mean, that run has been removed earlier
                if "NotFound" not in str(exe):
                    click.echo(TEXTS["incomplete_purge_error_msg"].format(experiment_name=experiment_name))
                    raise exe
            try:
                # clear run logs
                logger.debug(f"Clearing logs for {run.name} run.")
                k8s_es_client.delete_logs_for_run(run=run.name, namespace=namespace)
            except Exception:
                logger.exception("Error during clearing run logs.")

            # CAN-1099 - docker garbage collector has errors that prevent from correct removal of images
            # try:
                # try to remove images from docker registry
            #    delete_images_for_experiment(exp_name=run.name)
            # except Exception:
            #    logger.exception("Error during removing images.")

        if cancel_whole_experiment and not not_purged_runs:
            try:
                kubectl.delete_k8s_object("experiment", exp_name)
            except Exception:
                # problems during deleting experiments are hidden as if runs were
                # cancelled user doesn't have a possibility to remove them
                logger.exception("Error during purging experiment.")

    except Exception:
        logger.exception("Error during purging experiment.")
        return purged_runs, not_purged_runs

    return purged_runs, not_purged_runs


def cancel_experiment(exp_name: str, runs_to_cancel: List[Run], namespace: str) -> Tuple[List[Run], List[Run]]:
    """
    Cancel experiment with a given name by cancelling runs given as a parameter. If given experiment
    contains more runs than is in the list of runs - experiment's state remains intact.

    :param exp_name: name of an experiment to which belong runs passed in run_list parameter
    :param runs_to_cancel: list of runs that should be deleted, they have to belong to exp_name experiment
    :param namespace: namespace where experiment is located
    :return: two list - first contains runs that were cancelled successfully, second - those which weren't
    """
    logger.debug(f"Cancelling {exp_name} experiment ...")

    deleted_runs = []
    not_deleted_runs = []

    experiment = get_experiment(name=exp_name, namespace=namespace)
    if not experiment:
        raise RuntimeError(TEXTS["get_experiment_error_msg"])

    experiment_runs = list_runs(namespace=namespace, exp_name_filter=exp_name, excl_state=RunStatus.CANCELLED)
    # check whether experiment has more runs that should be cancelled
    cancel_whole_experiment = (len(experiment_runs) == len(runs_to_cancel))
    if cancel_whole_experiment:
        experiment.state = ExperimentStatus.CANCELLING
        update_experiment(experiment, namespace)

    try:
        deleted_runs, not_deleted_runs = cancel_experiment_runs(runs_to_cancel=runs_to_cancel, namespace=namespace)

        if cancel_whole_experiment and not not_deleted_runs:
            try:
                # change an experiment state to CANCELLED
                experiment.state = ExperimentStatus.CANCELLED
                update_experiment(experiment, namespace)
            except Exception:
                # problems during deleting experiments are hidden as if runs were
                # cancelled user doesn't have a possibility to remove them
                logger.exception("Error during cancelling Experiment resource.")

    except Exception:
        logger.exception("Error during cancelling experiment.")
        return deleted_runs, not_deleted_runs

    return deleted_runs, not_deleted_runs


def cancel_experiment_runs(runs_to_cancel: List[Run], namespace: str) -> Tuple[List[Run], List[Run]]:
    """
    Cancel given list of Runs belonging to a single namespace.
    :param runs_to_cancel: Runs to be cancelled
    :param namespace: namespace where Run instances reside
    :return: tuple of list containing successfully Runs and list containing Runs that were not cancelled
    """
    deleted_runs = []
    not_deleted_runs = []
    try:
        for run in runs_to_cancel:
            logger.debug(f"Cancelling {run.name} run ...")
            click.echo(TEXTS["canceling_runs_start_msg"].format(run_name=run.name, experiment_name=experiment_name))
            try:
                # if run status is cancelled - omit the following steps
                if run.state != RunStatus.CANCELLED:
                    delete_helm_release(release_name=run.name, namespace=namespace, purge=False)
                    # change a run state to CANCELLED
                    click.echo(TEXTS["cancel_setting_status_msg"].format(run_name=run.name))
                    run.state = RunStatus.CANCELLED
                    update_run(run, namespace)
                deleted_runs.append(run)
            except Exception:
                logger.exception(TEXTS["incomplete_cancel_error_msg"]
                                 .format(run_name=run.name, experiment_name=experiment_name))
                click.echo(TEXTS["incomplete_cancel_error_msg"]
                           .format(run_name=run.name, experiment_name=experiment_name))
                not_deleted_runs.append(run)

    except Exception:
        logger.exception("Error during cancelling experiments")
        return deleted_runs, not_deleted_runs

    return deleted_runs, not_deleted_runs


def cancel_pods_mode(namespace: str, run_name: str = None, pod_ids: str = None, pod_status: str = None):
    namespace_pods = k8s_pods.list_pods(namespace=namespace)

    runs_only_pods = [pod for pod in namespace_pods if 'runName' in pod.labels]

    filtered_pods = runs_only_pods

    if run_name:
        run_name_match_pods = []
        for pod in runs_only_pods:
            if re.match(run_name, pod.labels['runName']):
                run_name_match_pods.append(pod)

        filtered_pods = run_name_match_pods

    if pod_ids:
        pod_ids_match_pods = []
        pod_ids_array = pod_ids.split(',')
        for pod in filtered_pods:
            if pod.name in pod_ids_array:
                pod_ids_match_pods.append(pod)

        filtered_pods = pod_ids_match_pods

    if pod_status:
        status_filtered_pods = []
        try:
            converted_pod_status = PodStatus(pod_status.upper())
        except ValueError:
            handle_error(
                user_msg=TEXTS["bad_pod_status_passed"].format(status_passed=pod_status,
                                                               available_statuses=PodStatus.all_members())
            )
            exit(1)
            return

        for pod in filtered_pods:
            if pod.status == converted_pod_status:
                status_filtered_pods.append(pod)

        filtered_pods = status_filtered_pods

    if not filtered_pods:
        handle_error(user_msg=TEXTS["lack_of_pods_error_msg"])
        exit(1)

    click.echo(TEXTS["will_be_purged_list_header"].format(experiment_name_plural='pods'))
    for pod in filtered_pods:
        click.echo(f"     - {pod.name}")

    if not click.confirm(TEXTS["confirm_cancel_msg"].format(experiment_name_plural='pods')):
        handle_error(
            user_msg=TEXTS["cancellation_aborted_msg"].format(
                experiment_name_plural='pods'
            )
        )
        exit(2)

    deleted_pods = []
    not_deleted_pods = []

    for pod in filtered_pods:
        click.echo(TEXTS["canceling_pods_msg"].format(pod_name=pod.name))
        try:
            pod.delete()
            deleted_pods.append(pod)
        except Exception:
            handle_error(logger, TEXTS["other_pod_cancelling_error_msg"])
            not_deleted_pods.append(pod)

    if deleted_pods:
        click.echo(TEXTS["successfully_cancelled_list_header"].format(experiment_name_plural='pods'))
        for pod in deleted_pods:
            click.echo(f"     - {pod.name}")

    if not_deleted_pods:
        click.echo(TEXTS["failed_to_cancel_list_header"].format(experiment_name_plural='pods'))
        for pod in not_deleted_pods:
            click.echo(f"     - {pod.name}")
        sys.exit(1)
