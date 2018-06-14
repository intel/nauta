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
from platform_resources.experiments import list_experiments, update_experiment
from util.logger import initialize_logger

HELP = "Cancels experiment/s chosen based on criteria given as a parameter."
HELP_P = "If given - all information concerning experiments is removed from the system."

log = initialize_logger(__name__)


@click.command(short_help=HELP, cls=AliasCmd, alias='c')
@click.argument("name")
@click.option('-p', '--purge', default=None, help=HELP_P, is_flag=True)
@common_options()
@pass_state
def cancel(state: State, name: str, purge: bool):
    """
    Cancels chosen experiments based on a name provided as a parameter.
    """

    # check whether we have runs with a given name
    current_namespace = get_current_namespace()
    try:
        list_of_all_runs = list_runs(namespace=current_namespace, name_filter=name)
    except Exception:
        err_message = "Problems during loading a list of experiments."
        log.exception(err_message)
        click.echo(err_message)
        sys.exit(1)

    if not list_of_all_runs:
        click.echo("Lack of experiments fulfilling given criteria.")
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
            click.echo("Experiments fulfilling given criteria have been cancelled already.")
            sys.exit(1)
        elif len(list_of_runs_to_be_deleted) != len(list_of_all_runs):
            click.echo("The following experiments have been cancelled already:")
            for name in names_of_cancelled_runs:
                click.echo(f"     - {name}")
            click.echo("The following experiments can still be cancelled:")
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
        else:
            click.echo("The following experiments will be cancelled:")
            for name in list_of_runs_to_be_deleted:
                click.echo(f"     - {name.name}")
    else:
        list_of_runs_to_be_deleted = list_of_all_runs
        click.echo("The following experiments will be purged:")
        for name in list_of_runs_to_be_deleted:
            click.echo(f"     - {name.name}")

    if not click.confirm("Do you want to continue with cancellation of those experiments?",):
        click.echo("Operation of cancellation of experiments was aborted.")
        sys.exit(2)

    # group runs by experiments
    exp_with_runs = defaultdict(list)

    for run in list_of_runs_to_be_deleted:
        exp_with_runs[run.experiment_name].append(run)

    config.load_kube_config()
    v1 = client.CoreV1Api()

    deleted_runs = []
    not_deleted_runs = []

    for exp_name, run_list in exp_with_runs.items():
        try:
            del_runs, not_del_runs = cancel_experiment(exp_name=exp_name, run_list=run_list, v1=v1,
                                                       namespace=current_namespace, purge=purge)
            deleted_runs.extend(del_runs)
            not_deleted_runs.extend(not_del_runs)
        except Exception as exe:
            log.exception("Error during cancelling an experiment.")
            not_deleted_runs.extend(run_list)

    if deleted_runs:
        click.echo("The following experiments were cancelled succesfully:")
        for run in deleted_runs:
            click.echo(f"     - {run.name}")

    if not_deleted_runs:
        click.echo("The following experiments weren't cancelled properly:")
        for run in not_deleted_runs:
            click.echo(f"     - {run.name}")
        sys.exit(1)


def cancel_experiment(exp_name: str, run_list: List[Run], v1: client.CoreV1Api, purge: bool=False, namespace: str="") \
        -> Tuple[List[Run], List[Run]]:
    """
    Cancel experiment with a given name by cancelling runs given as a parameter. If given experiment
    contains more runs than is in the list of runs - experiment's state remains intact.

    :param exp_name: name of an experiment to which belong runs passed in run_list parameter
    :param run_list: list of runs that should be deleted, they have to belong to exp_name experiment
    :param v1: K8s api object
    :param purge: if True - function removes all data related to an experiment
    :param namespace: namespace where experiment is located
    :return: two list - first contains runs that were cancelled successfully, second - those which weren't
    """
    log.debug(f"Cancelling {exp_name} experiment ...")

    deleted_runs = []
    not_deleted_runs = []
    # check whether experiment has more runs that should be cancelled
    if purge:
        exp_runs_list = list_runs(namespace=namespace, exp_name_filter=exp_name)
    else:
        exp_runs_list = list_runs(namespace=namespace, exp_name_filter=exp_name, excl_state=RunStatus.CANCELLED)

    cancel_experiment = (len(exp_runs_list) == len(run_list))

    if cancel_experiment:
        experiment_list = list_experiments(namespace=namespace, name_filter=exp_name)

        if not experiment_list:
            raise RuntimeError("Error during loading experiment's data")

        experiment = experiment_list[0]
        experiment.state = ExperimentStatus.CANCELLING
        update_experiment(experiment, namespace)

    try:
        for run in run_list:
            click.echo(f"Cancelling {run.name} experiment ...")
            # delete all main objects related to run
            list_of_pods = v1.list_namespaced_pod(watch=False, namespace=namespace,
                                                  label_selector=f"runName={run.name}")

            already_deleted = set()
            click.echo(f"Deleting objects related to {run.name} experiment ...")
            all_objects_deleted = True
            for pod in list_of_pods.items:
                owner_name, owner_kind = get_owners_data(pod)
                owner_key = f"{owner_name}{owner_kind}"
                if owner_key not in already_deleted:
                    try:
                        kubectl.delete_k8s_object(owner_kind, owner_name)
                        already_deleted.add(owner_key)
                    except Exception as exe:
                        log.exception("Error during removal of a k8s object.")
                        all_objects_deleted = False

            if all_objects_deleted:
                # purge - only if all previous steps were successful
                if purge:
                    # remove docker images related to experiment

                    try:
                        # delete run
                        kubectl.delete_k8s_object("run", run.name)
                    except Exception as exe:
                        not_deleted_runs.append(run)
                        log.exception("Error during purging runs.")
                        # occurence of NotFound error may mean, that run has been removed earlier
                        if "NotFound" not in str(exe):
                            click.echo("Not all experiment's components were removed properly.")
                            raise exe

                else:
                    # change a run state to CANCELLED
                    click.echo(f"Setting experiment status to CANCELLED ...")
                    run.state = RunStatus.CANCELLED
                    update_run(run, namespace)

                deleted_runs.append(run)
            else:
                click.echo(f"Not all components of {run.name} experiment were deleted ...")
                click.echo("Experiment remains in its previous state.")
                not_deleted_runs.append(run)

        if cancel_experiment and not not_deleted_runs:
            try:
                if purge:
                    # delete experiment
                    kubectl.delete_k8s_object("experiment", exp_name)
                else:
                    # change an experiment state to CANCELLED
                    experiment.state = ExperimentStatus.CANCELLED
                    update_experiment(experiment, namespace)
            except Exception as exe:
                # problems during deleting experiments are hidden as if runs were
                # cancelled user doesn't have a possibility to remove them
                log.exception("Error during purging experiments.")

    except Exception:
        log.exception("Error during cancelling experiments")
        return deleted_runs, not_deleted_runs

    return deleted_runs, not_deleted_runs


def get_owners_data(pod: V1Pod) -> (str, str):
    owner_kind = pod.metadata.owner_references[0].kind
    owner_name = pod.metadata.owner_references[0].name
    return owner_name, owner_kind
