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
from datetime import datetime
from enum import Enum
import re
import sys
from sys import exit
from typing import List, Tuple

import click

from commands.experiment.common import RunKinds
import util.k8s.kubectl as kubectl
from cli_state import common_options, pass_state, State
from util.aliascmd import AliasCmd
from util.k8s.k8s_info import get_current_namespace
from platform_resources.run import Run, RunStatus
from platform_resources.experiment import ExperimentStatus, Experiment
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from util.app_names import NAUTAAppNames
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.helm import delete_helm_release
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.k8s import pods as k8s_pods
from util.logger import initialize_logger
from util.spinner import spinner
from util.system import handle_error
from cli_text_consts import ExperimentCancelCmdTexts as Texts
from util.k8s.k8s_info import PodStatus


logger = initialize_logger(__name__)

experiment_name = 'experiment'
experiment_name_plural = 'experiments'


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='c', options_metavar='[options]')
@click.argument("name", required=False, metavar="[name]")
@click.option('-m', '--match', help=Texts.HELP_M)
@click.option('-p', '--purge', help=Texts.HELP_P, is_flag=True)
@click.option('-i', '--pod-ids', help=Texts.HELP_I)
@click.option('-s', '--pod-status', help=Texts.HELP_S.format(available_statuses=PodStatus.all_members()))
@common_options()
@pass_state
def cancel(state: State, name: str, match: str, purge: bool, pod_ids: str, pod_status: str,
           listed_runs_kinds: List[Enum] = None):
    """
    Cancels chosen experiments based on a name provided as a parameter.
    """
    if not listed_runs_kinds:
        listed_runs_kinds = [RunKinds.TRAINING, RunKinds.JUPYTER]

    # check whether we have runs with a given name
    if name and match:
        handle_error(user_msg=Texts.NAME_M_BOTH_GIVEN_ERROR_MSG)
        exit(1)

    if not name and not match:
        handle_error(user_msg=Texts.NAME_M_NONE_GIVEN_ERROR_MSG)
        exit(1)

    current_namespace = get_current_namespace()

    if pod_ids or pod_status:
        if not name:
            name = match

        cancel_pods_mode(namespace=current_namespace, run_name=name, pod_ids=pod_ids, pod_status=pod_status)
        exit(0)

    search_for_experiment = False
    exp_to_be_cancelled = None

    if name:
        exp_to_be_cancelled = Experiment.get(namespace=current_namespace, name=name)
        exp_to_be_cancelled_kind = RunKinds(exp_to_be_cancelled.metadata['labels'].get('runKind')) \
            if exp_to_be_cancelled else None
        exp_to_be_cancelled = exp_to_be_cancelled if exp_to_be_cancelled_kind in listed_runs_kinds else None

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
            list_of_all_runs = Run.list(namespace=current_namespace, exp_name_filter=[name],
                                        run_kinds_filter=listed_runs_kinds)
        else:
            list_of_all_runs = Run.list(namespace=current_namespace, name_filter=name,
                                        run_kinds_filter=listed_runs_kinds)
    except Exception:
        handle_error(logger, Texts.LIST_RUNS_ERROR_MSG.format(experiment_name_plural=experiment_name_plural),
                     Texts.LIST_RUNS_ERROR_MSG.format(experiment_name_plural=experiment_name_plural))
        exit(1)

    # Handle cancellation of experiments with no associated Runs
    if exp_to_be_cancelled and not list_of_all_runs:
        cancel_uninitialized_experiment(experiment=exp_to_be_cancelled, namespace=current_namespace,
                                        purge=purge)
    # If no experiment and no runs were matched, throw an error
    elif not [run for run in list_of_all_runs if run.state in list_of_applicable_states]:
        handle_error(user_msg=Texts.LACK_OF_EXPERIMENTS_ERROR_MSG.format(
            experiment_name_plural=experiment_name_plural,
            experiment_name=experiment_name))
        exit(1)

    # check whether we have at least one experiment in state other than CANCELLED
    list_of_runs_to_be_deleted = []
    names_of_cancelled_runs = []

    if not purge:
        # check whether we have at least one experiment in state other than CANCELLED
        for run in list_of_all_runs:
            if run.state in list_of_applicable_states:
                list_of_runs_to_be_deleted.append(run)
            else:
                names_of_cancelled_runs.append(run.name)

        if not list_of_runs_to_be_deleted:
            handle_error(
                user_msg=Texts.EXPERIMENTS_ALREADY_CANCELLED_ERROR_MSG.format(
                    experiment_name_plural=experiment_name_plural,
                    operation_word=Texts.DELETE_OPERATION["deleted"] if experiment_name_plural == 'pods'
                    else Texts.CANCEL_OPERATION["cancelled"]
                )
            )
            exit(1)
        elif len(list_of_runs_to_be_deleted) != len(list_of_all_runs):
            click.echo(Texts.ALREADY_CANCELLED_LIST_HEADER.format(experiment_name_plural=experiment_name_plural,
                                                                  operation_word=Texts.DELETE_OPERATION[
                                                                      "deleted"] if experiment_name_plural == 'pods'
                                                                  else Texts.CANCEL_OPERATION["cancelled"]
                                                                  ))
            for name in names_of_cancelled_runs:
                click.echo(f"     - {name}")
            click.echo(Texts.CAN_BE_CANCELLED_LIST_HEADER.format(experiment_name_plural=experiment_name_plural,
                                                                 operation_word=Texts.DELETE_OPERATION[
                                                                     "deleted"] if experiment_name_plural == 'pods'
                                                                 else Texts.CANCEL_OPERATION["cancelled"]
                                                                 ))
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
        else:
            click.echo(Texts.WILL_BE_CANCELLED_LIST_HEADER.format(experiment_name_plural=experiment_name_plural,
                                                                  operation_word=Texts.DELETE_OPERATION[
                                                                      "deleted"] if experiment_name_plural == 'pods'
                                                                  else Texts.CANCEL_OPERATION["cancelled"]
                                                                  ))
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
    else:
        list_of_runs_to_be_deleted = list_of_all_runs
        click.echo(Texts.WILL_BE_PURGED_LIST_HEADER.format(experiment_name_plural=experiment_name_plural,
                                                           operation_word=Texts.DELETE_OPERATION[
                                                               "deleted"] if experiment_name_plural == 'pods'
                                                           else Texts.CANCEL_OPERATION["cancelled"]
                                                           ))
        for name in list_of_runs_to_be_deleted:
            click.echo(f"     - {name.name}")

    if not click.confirm(Texts.CONFIRM_CANCEL_MSG.format(experiment_name_plural=experiment_name_plural,
                                                         operation_word=Texts.DELETE_OPERATION[
                                                             "deletion"] if experiment_name_plural == 'pods'
                                                         else Texts.CANCEL_OPERATION["cancellation"]
                                                         )):
        handle_error(
            user_msg=Texts.CANCELLATION_ABORTED_MSG.format(
                experiment_name_plural=experiment_name_plural,
                operation_word=Texts.DELETE_OPERATION["deletion"] if experiment_name_plural == 'pods'
                else Texts.CANCEL_OPERATION["cancellation"]
            )
        )
        exit(0)

    # group runs by experiments
    exp_with_runs = defaultdict(list)

    for run in list_of_runs_to_be_deleted:
        exp_with_runs[run.experiment_name].append(run)

    deleted_runs = []
    not_deleted_runs = []

    if purge:
        # Connect to elasticsearch in order to purge run logs
        try:
            with K8sProxy(NAUTAAppNames.ELASTICSEARCH) as proxy:
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
                        handle_error(logger, Texts.OTHER_CANCELLING_ERROR_MSG)
                        not_deleted_runs.extend(run_list)
        except K8sProxyCloseError:
            handle_error(logger, Texts.PROXY_CLOSING_ERROR_LOG_MSG, Texts.PROXY_CLOSING_ERROR_USER_MSG)
            exit(1)
        except LocalPortOccupiedError as exe:
            handle_error(logger, Texts.PORT_OCCUPIED_ERROR_LOG_MSG,
                         Texts.PORT_OCCUPIED_ERROR_USER_MSG.format(exception_message=exe.message))
            exit(1)
        except K8sProxyOpenError:
            handle_error(logger, Texts.PROXY_OPEN_ERROR_MSG, Texts.PROXY_OPEN_ERROR_MSG)
            exit(1)
    else:
        for exp_name, run_list in exp_with_runs.items():
            try:
                exp_del_runs, exp_not_del_runs = cancel_experiment(exp_name=exp_name, runs_to_cancel=run_list,
                                                                   namespace=current_namespace)
                deleted_runs.extend(exp_del_runs)
                not_deleted_runs.extend(exp_not_del_runs)
            except Exception:
                handle_error(logger, Texts.OTHER_CANCELLING_ERROR_MSG)
                not_deleted_runs.extend(run_list)

    if deleted_runs:
        click.echo(Texts.SUCCESSFULLY_CANCELLED_LIST_HEADER.format(experiment_name_plural=experiment_name_plural,
                                                                   operation_word=Texts.DELETE_OPERATION[
                                                                       "deleted"] if experiment_name_plural == 'pods'
                                                                   else Texts.CANCEL_OPERATION["cancelled"]
                                                                   ))
        for run in deleted_runs:
            click.echo(f"     - {run.name}")

    if not_deleted_runs:
        click.echo(Texts.FAILED_TO_CANCEL_LIST_HEADER.format(experiment_name_plural=experiment_name_plural,
                                                             operation_word=Texts.DELETE_OPERATION[
                                                                 "deleted"] if experiment_name_plural == 'pods'
                                                             else Texts.CANCEL_OPERATION["cancelled"]
                                                             ))
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

    experiment = Experiment.get(name=exp_name, namespace=namespace)
    if not experiment:
        raise RuntimeError(Texts.GET_EXPERIMENT_ERROR_MSG)

    experiment_runs = Run.list(namespace=namespace, exp_name_filter=[exp_name])
    # check whether experiment has more runs that should be cancelled
    cancel_whole_experiment = (len(experiment_runs) == len(runs_to_purge))
    if cancel_whole_experiment:
        experiment.state = ExperimentStatus.CANCELLING
        experiment.update()

    try:
        cancelled_runs, not_cancelled_runs = cancel_experiment_runs(runs_to_cancel=runs_to_purge, namespace=namespace)
        not_purged_runs = not_cancelled_runs
        for run in cancelled_runs:
            logger.debug(f"Purging {run.name} run ...")
            click.echo(Texts.PURGING_START_MSG.format(run_name=run.name))
            try:
                with spinner(text=Texts.PURGING_PROGRESS_MSG.format(run_name=run.name)):
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
                    click.echo(Texts.INCOMPLETE_PURGE_ERROR_MSG.format(experiment_name=experiment_name))
                    raise exe
            try:
                # clear run logs
                logger.debug(f"Clearing logs for {run.name} run.")
                with spinner(text=Texts.PURGING_LOGS_PROGRESS_MSG.format(run_name=run.name)):
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

    experiment = Experiment.get(name=exp_name, namespace=namespace)
    if not experiment:
        raise RuntimeError(Texts.GET_EXPERIMENT_ERROR_MSG)

    experiment_runs = Run.list(namespace=namespace, exp_name_filter=[exp_name], excl_state=RunStatus.CANCELLED)
    # check whether experiment has more runs that should be cancelled
    cancel_whole_experiment = (len(experiment_runs) == len(runs_to_cancel))
    if cancel_whole_experiment:
        experiment.state = ExperimentStatus.CANCELLING
        experiment.update()

    try:
        deleted_runs, not_deleted_runs = cancel_experiment_runs(runs_to_cancel=runs_to_cancel, namespace=namespace)

        if cancel_whole_experiment and not not_deleted_runs:
            try:
                # change an experiment state to CANCELLED
                experiment.state = ExperimentStatus.CANCELLED
                experiment.update()
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
            click.echo(Texts.CANCELING_RUNS_START_MSG.format(run_name=run.name, experiment_name=experiment_name))
            try:
                # if run status is cancelled - omit the following steps
                if run.state != RunStatus.CANCELLED:
                    with spinner(text=Texts.CANCEL_SETTING_STATUS_MSG.format(run_name=run.name)):
                        delete_helm_release(release_name=run.name, namespace=namespace, purge=False)
                        # change a run state to CANCELLED
                        run.state = RunStatus.CANCELLED
                        run.end_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                        run.update()
                deleted_runs.append(run)
            except Exception:
                logger.exception(Texts.INCOMPLETE_CANCEL_ERROR_MSG
                                 .format(run_name=run.name, experiment_name=experiment_name))
                click.echo(Texts.INCOMPLETE_CANCEL_ERROR_MSG
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
                user_msg=Texts.BAD_POD_STATUS_PASSED.format(status_passed=pod_status,
                                                            available_statuses=PodStatus.all_members())
            )
            exit(1)
            return

        for pod in filtered_pods:
            if pod.status == converted_pod_status:
                status_filtered_pods.append(pod)

        filtered_pods = status_filtered_pods

    if not filtered_pods:
        handle_error(user_msg=Texts.LACK_OF_PODS_ERROR_MSG)
        exit(1)

    click.echo(Texts.WILL_BE_PURGED_LIST_HEADER.format(experiment_name_plural='pods',
                                                       operation_word=Texts.DELETE_OPERATION[
                                                           "deleted"]
                                                       ))
    for pod in filtered_pods:
        click.echo(f"     - {pod.name}")

    if not click.confirm(Texts.CONFIRM_CANCEL_MSG.format(experiment_name_plural='pods',
                                                         operation_word=Texts.DELETE_OPERATION["deletion"])):
        handle_error(
            user_msg=Texts.CANCELLATION_ABORTED_MSG.format(
                experiment_name_plural='pods',
                operation_word=Texts.DELETE_OPERATION["deletion"]
            )
        )
        exit(0)

    deleted_pods = []
    not_deleted_pods = []

    for pod in filtered_pods:
        click.echo(Texts.CANCELING_PODS_MSG.format(pod_name=pod.name))
        try:
            pod.delete()
            deleted_pods.append(pod)
        except Exception:
            handle_error(logger, Texts.OTHER_POD_CANCELLING_ERROR_MSG)
            not_deleted_pods.append(pod)

    if deleted_pods:
        click.echo(Texts.SUCCESSFULLY_CANCELLED_LIST_HEADER.format(experiment_name_plural='pods',
                                                                   operation_word=Texts.DELETE_OPERATION["deleted"]))
        for pod in deleted_pods:
            click.echo(f"     - {pod.name}")

    if not_deleted_pods:
        click.echo(Texts.FAILED_TO_CANCEL_LIST_HEADER.format(experiment_name_plural='pods',
                                                             operation_word=Texts.DELETE_OPERATION["deleted"]))
        for pod in not_deleted_pods:
            click.echo(f"     - {pod.name}")
        sys.exit(1)


def cancel_uninitialized_experiment(experiment: Experiment, namespace: str, purge: bool):
    click.echo(Texts.UNINITIALIZED_EXPERIMENT_CANCEL_MSG.format(experiment_name=experiment.name))
    if not click.confirm(Texts.CONFIRM_CANCEL_MSG.format(experiment_name_plural=experiment_name_plural,
                                                         operation_word=Texts.DELETE_OPERATION[
                                                             "deletion"] if experiment_name_plural == 'pods'
                                                         else Texts.CANCEL_OPERATION["cancellation"]
                                                         )):
        handle_error(
            user_msg=Texts.CANCELLATION_ABORTED_MSG.format(
                experiment_name_plural=experiment_name_plural,
                operation_word=Texts.DELETE_OPERATION["deletion"] if experiment_name_plural == 'pods'
                else Texts.CANCEL_OPERATION["cancellation"]
            )
        )
        exit(0)

    try:
        if purge:
            click.echo(Texts.PURGING_START_MSG.format(run_name=experiment.name))
            experiment.delete()
        else:
            click.echo(Texts.CANCELING_RUNS_START_MSG.format(experiment_name=experiment.name,
                                                             run_name=''))
            experiment.state = ExperimentStatus.CANCELLED
            experiment.update()
    except Exception:
        handle_error(logger, Texts.OTHER_CANCELLING_ERROR_MSG)
        exit(1)

    exit(0)
