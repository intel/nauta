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
from collections import defaultdict

import click
from kubernetes import client, config
from kubernetes.client.models import V1Pod
from typing import List, Tuple

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
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.logger import initialize_logger
from util.docker import delete_images_for_experiment

HELP = "Cancels experiment/s chosen based on criteria given as a parameter."
HELP_P = "If given, then all information concerning all experiments, completed and currently running, " \
         "is removed from the system."
HELP_M = "If given, command searches for experiments matching the value of this option."

log = initialize_logger(__name__)

experiment_name = 'experiment'
experiment_name_plural = 'experiments'


@click.command(short_help=HELP, cls=AliasCmd, alias='c')
@click.argument("name", required=False)
@click.option('-m', '--match', default=None, help=HELP_M)
@click.option('-p', '--purge', default=None, help=HELP_P, is_flag=True)
@common_options()
@pass_state
def cancel(state: State, name: str, match: str, purge: bool):
    """
    Cancels chosen experiments based on a name provided as a parameter.
    """

    # check whether we have runs with a given name

    if name and match:
        click.echo("Both name and -m option cannot be given. Please choose one of them.")
        sys.exit(1)
    elif not name and not match:
        click.echo("Name or -m option must be given. Please pass one of them.")
        sys.exit(1)

    current_namespace = get_current_namespace()
    search_for_experiment = False

    if name:
        exp_to_be_cancelled = get_experiment(namespace=current_namespace, name=name)

        if exp_to_be_cancelled:
            search_for_experiment = True
        else:
            name = f"^{name}$"
    else:
        name = match

    try:
        if search_for_experiment:
            list_of_all_runs = list_runs(namespace=current_namespace, exp_name_filter=name)
        else:
            list_of_all_runs = list_runs(namespace=current_namespace, name_filter=name)
    except Exception:
        err_message = f"Problems during loading a list of {experiment_name_plural}."
        log.exception(err_message)
        click.echo(err_message)
        sys.exit(1)

    if not list_of_all_runs:
        click.echo(f"Lack of {experiment_name_plural} fulfilling given criteria."
                   f" Name or match string parameters do not match any existing {experiment_name}."
                   f" Run 'dlsctl exp list' to find out what are the names of existing {experiment_name_plural}.")
        sys.exit(1)

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
            click.echo(f"{experiment_name_plural} fulfilling given criteria have been cancelled already.")
            sys.exit(1)
        elif len(list_of_runs_to_be_deleted) != len(list_of_all_runs):
            click.echo(f"The following {experiment_name_plural} have been cancelled already:")
            for name in names_of_cancelled_runs:
                click.echo(f"     - {name}")
            click.echo(f"The following {experiment_name_plural} can still be cancelled:")
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
        else:
            click.echo(f"The following {experiment_name_plural} will be cancelled:")
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
    else:
        list_of_runs_to_be_deleted = list_of_all_runs
        click.echo(f"The following {experiment_name_plural} will be purged:")
        for name in list_of_runs_to_be_deleted:
            click.echo(f"     - {name.name}")

    if not click.confirm(f"Do you want to continue with cancellation of those {experiment_name_plural}?", ):
        click.echo(f"Operation of cancellation of {experiment_name_plural} was aborted.")
        sys.exit(2)

    # group runs by experiments
    exp_with_runs = defaultdict(list)

    for run in list_of_runs_to_be_deleted:
        exp_with_runs[run.experiment_name].append(run)

    config.load_kube_config()
    k8s_api = client.CoreV1Api()
    k8s_apps_api = client.AppsV1Api()

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
                                                                          runs_to_purge=run_list, k8s_api=k8s_api,
                                                                          namespace=current_namespace,
                                                                          k8s_es_client=es_client,
                                                                          k8s_apps_api=k8s_apps_api)
                        deleted_runs.extend(exp_del_runs)
                        not_deleted_runs.extend(exp_not_del_runs)
                    except Exception:
                        log.exception("Error during cancelling an experiment.")
                        not_deleted_runs.extend(run_list)
        except K8sProxyCloseError:
            log.exception("Error during closing of a proxy for elasticsearch.")
            click.echo("Elasticsearch proxy hasn't been closed properly. "
                       "Check whether it still exists, if yes - close it manually.")
            sys.exit(1)
        except LocalPortOccupiedError as exe:
            log.exception("Error during creation of proxy - port is occupied.")
            click.echo(f"Error during creation of a proxy for elasticsearch. {exe.message}")
            sys.exit(1)
        except K8sProxyOpenError:
            log.exception("Error during creation of a proxy for elasticsearch.")
            click.echo("Error during creation of a proxy for elasticsearch.")
            sys.exit(1)
    else:
        for exp_name, run_list in exp_with_runs.items():
            try:
                exp_del_runs, exp_not_del_runs = cancel_experiment(exp_name=exp_name, runs_to_cancel=run_list,
                                                                   k8s_api=k8s_api, namespace=current_namespace,
                                                                   k8s_apps_api=k8s_apps_api)
                deleted_runs.extend(exp_del_runs)
                not_deleted_runs.extend(exp_not_del_runs)
            except Exception:
                log.exception("Error during cancelling an experiment.")
                not_deleted_runs.extend(run_list)

    if deleted_runs:
        click.echo(f"The following {experiment_name_plural} were cancelled succesfully:")
        for run in deleted_runs:
            click.echo(f"     - {run.name}")

    if not_deleted_runs:
        click.echo(f"The following {experiment_name_plural} weren't cancelled properly:")
        for run in not_deleted_runs:
            click.echo(f"     - {run.name}")
        sys.exit(1)


def purge_experiment(exp_name: str, runs_to_purge: List[Run], k8s_api: client.CoreV1Api,
                     k8s_es_client: K8sElasticSearchClient, k8s_apps_api: client.AppsV1Api,
                     namespace: str="") -> Tuple[List[Run], List[Run]]:
    """
       Purge experiment with a given name by cancelling runs given as a parameter. If given experiment
       contains more runs than is in the list of runs - experiment's state remains intact.

       :param exp_name: name of an experiment to which belong runs passed in run_list parameter
       :param runs_to_purge: list of runs that should be purged, they have to belong to exp_name experiment
       :param k8s_api: K8s api object
       :param k8s_es_client: Kubernetes ElasticSearch client
       :param k8s_apps_api: K8s_apps api object
       :param namespace: namespace where experiment is located
       :return: two list - first contains runs that were cancelled successfully, second - those which weren't
       """
    log.debug(f"Purging {exp_name} experiment ...")

    purged_runs = []
    not_purged_runs = []

    experiment = get_experiment(name=exp_name, namespace=namespace)
    if not experiment:
        raise RuntimeError("Error during loading experiment's data.")

    experiment_runs = list_runs(namespace=namespace, exp_name_filter=exp_name)
    # check whether experiment has more runs that should be cancelled
    cancel_whole_experiment = (len(experiment_runs) == len(runs_to_purge))
    if cancel_whole_experiment:
        experiment.state = ExperimentStatus.CANCELLING
        update_experiment(experiment, namespace)

    try:
        cancelled_runs, not_cancelled_runs = cancel_experiment_runs(runs_to_cancel=runs_to_purge,
                                                                    k8s_api=k8s_api, namespace=namespace,
                                                                    k8s_apps_api=k8s_apps_api)
        not_purged_runs = not_cancelled_runs
        for run in cancelled_runs:
            log.debug(f"Purging {run.name} run ...")
            click.echo(f"Purging {run.name} experiment ...")
            try:
                # delete run
                kubectl.delete_k8s_object("run", run.name)
                purged_runs.append(run)
            except Exception as exe:
                not_purged_runs.append(run)
                log.exception("Error during purging runs.")
                # occurence of NotFound error may mean, that run has been removed earlier
                if "NotFound" not in str(exe):
                    click.echo(f"Not all {experiment_name}'s components were removed properly.")
                    raise exe
            try:
                # clear run logs
                log.debug(f"Clearing logs for {run.name} run.")
                k8s_es_client.delete_logs_for_run(run=run.name)
            except Exception:
                log.exception("Error during clearing run logs.")

            try:
                # try to remove images from docker registry
                delete_images_for_experiment(exp_name=run.name)
            except Exception:
                log.exception("Error during removing images.")

        if cancel_whole_experiment and not not_purged_runs:
            try:
                kubectl.delete_k8s_object("experiment", exp_name)
            except Exception:
                # problems during deleting experiments are hidden as if runs were
                # cancelled user doesn't have a possibility to remove them
                log.exception("Error during purging experiment.")

    except Exception:
        log.exception("Error during purging experiment.")
        return purged_runs, not_purged_runs

    return purged_runs, not_purged_runs


def cancel_experiment(exp_name: str, runs_to_cancel: List[Run], k8s_api: client.CoreV1Api,
                      k8s_apps_api: client.AppsV1Api, namespace: str="") -> Tuple[List[Run], List[Run]]:
    """
    Cancel experiment with a given name by cancelling runs given as a parameter. If given experiment
    contains more runs than is in the list of runs - experiment's state remains intact.

    :param exp_name: name of an experiment to which belong runs passed in run_list parameter
    :param runs_to_cancel: list of runs that should be deleted, they have to belong to exp_name experiment
    :param k8s_api: K8s api object
    :param k8s_apps_api: K8s_apps api object
    :param namespace: namespace where experiment is located
    :return: two list - first contains runs that were cancelled successfully, second - those which weren't
    """
    log.debug(f"Cancelling {exp_name} experiment ...")

    deleted_runs = []
    not_deleted_runs = []

    experiment = get_experiment(name=exp_name, namespace=namespace)
    if not experiment:
        raise RuntimeError("Error during loading experiment's data.")

    experiment_runs = list_runs(namespace=namespace, exp_name_filter=exp_name, excl_state=RunStatus.CANCELLED)
    # check whether experiment has more runs that should be cancelled
    cancel_whole_experiment = (len(experiment_runs) == len(runs_to_cancel))
    if cancel_whole_experiment:
        experiment.state = ExperimentStatus.CANCELLING
        update_experiment(experiment, namespace)

    try:
        deleted_runs, not_deleted_runs = cancel_experiment_runs(runs_to_cancel=runs_to_cancel,
                                                                k8s_api=k8s_api, namespace=namespace,
                                                                k8s_apps_api=k8s_apps_api)

        if cancel_whole_experiment and not not_deleted_runs:
            try:
                # change an experiment state to CANCELLED
                experiment.state = ExperimentStatus.CANCELLED
                update_experiment(experiment, namespace)
            except Exception:
                # problems during deleting experiments are hidden as if runs were
                # cancelled user doesn't have a possibility to remove them
                log.exception("Error during cancelling Experiment resource.")

    except Exception as e:
        log.exception("Error during cancelling experiment.")
        return deleted_runs, not_deleted_runs

    return deleted_runs, not_deleted_runs


def cancel_experiment_runs(runs_to_cancel: List[Run], k8s_api: client.CoreV1Api,
                           k8s_apps_api: client.AppsV1Api, namespace: str="") -> Tuple[List[Run], List[Run]]:
    """
    Cancel given list of Runs belonging to a single namespace.
    :param runs_to_cancel: Runs to be cancelled
    :param k8s_api: k8s API client instance
    :param k8s_apps_api: K8s_apps api object
    :param namespace: namespace where Run instances reside
    :return: tuple of list containing successfully Runs and list containing Runs that were not cancelled
    """
    deleted_runs = []
    not_deleted_runs = []
    try:
        for run in runs_to_cancel:
            log.debug(f"Cancelling {run.name} run ...")
            click.echo(f"Cancelling {run.name} {experiment_name} ...")

            all_objects_deleted = True

            # removal of jupyter notebooks experiments - in the future - if there is such need - it can
            # be generalized to any type of k8s objects
            list_of_deployments = k8s_apps_api.list_namespaced_deployment(watch=False, namespace=namespace,
                                                                          label_selector=f"runName={run.name}")

            if list_of_deployments.items:
                # jupyter notebook contains deployments
                for item in list_of_deployments.items:
                    click.echo(f"Deleting objects related to {run.name} {experiment_name} ...")
                    try:
                        kubectl.delete_k8s_object("Deployment", item.metadata.name)
                    except Exception:
                        log.exception("Error during removal of a k8s object.")
                        all_objects_deleted = False

                # and services - recognized by release and dls4e_app_name. To make it more general
                # we should put (and expect) runName label in any object that can be a part of an experiment
                list_of_services = k8s_api.list_namespaced_service(watch=False, namespace=namespace,
                                                                   label_selector=f"release={run.name}")
                for item in list_of_services.items:
                    try:
                        kubectl.delete_k8s_object("Service", item.metadata.name)
                    except Exception:
                        log.exception("Error during removal of a k8s object.")
                        all_objects_deleted = False
            else:
                # delete all main objects related to run
                list_of_pods = k8s_api.list_namespaced_pod(watch=False, namespace=namespace,
                                                           label_selector=f"runName={run.name}")

                already_deleted = set()
                click.echo(f"Deleting objects related to {run.name} {experiment_name} ...")
                for pod in list_of_pods.items:
                    owner_name, owner_kind = get_owners_data(pod)
                    owner_key = f"{owner_name}{owner_kind}"
                    if owner_key not in already_deleted:
                        try:
                            kubectl.delete_k8s_object(owner_kind, owner_name)
                            already_deleted.add(owner_key)
                        except Exception:
                            log.exception("Error during removal of a k8s object.")
                            all_objects_deleted = False

            if all_objects_deleted:
                # change a run state to CANCELLED
                click.echo(f"Setting {experiment_name} status to CANCELLED ...")
                run.state = RunStatus.CANCELLED
                update_run(run, namespace)
                deleted_runs.append(run)
            else:
                click.echo(f"Not all components of {run.name} {experiment_name} were deleted ...")
                click.echo("Experiment remains in its previous state.")
                not_deleted_runs.append(run)

    except Exception:
        log.exception("Error during cancelling experiments")
        return deleted_runs, not_deleted_runs

    return deleted_runs, not_deleted_runs


def get_owners_data(pod: V1Pod) -> (str, str):
    owner_kind = pod.metadata.owner_references[0].kind
    owner_name = pod.metadata.owner_references[0].name
    return owner_name, owner_kind
