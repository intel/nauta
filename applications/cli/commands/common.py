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

from collections import namedtuple
import dateutil.parser
import os
from typing import List, Generator
from sys import exit

import click
from tabulate import tabulate

from util.app_names import NAUTAAppNames
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.k8s_log_entry import LogEntry
from logs_aggregator.log_filters import SeverityLevel
from platform_resources.run import RunStatus, Run, RunKinds
from util.exceptions import InvalidRegularExpressionError, K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.logger import initialize_logger
from util.k8s.k8s_info import PodStatus, get_kubectl_current_context_namespace
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.spinner import spinner, NctlSpinner
from platform_resources.experiment import Experiment, ExperimentStatus
from util.system import handle_error, format_timestamp_for_cli
from cli_text_consts import CmdsCommonTexts as Texts, SPINNER_COLOR


logger = initialize_logger(__name__)

"""
A namedtuple representing uninitialized experiments in CLI.
"""
UninitializedExperimentCliModel = namedtuple('Experiment', ['name', 'parameters_spec', 'metrics',
                                                            'creation_timestamp', 'start_date', 'end_date', 'duration',
                                                            'submitter', 'status', 'template_name', 'template_version'])


def uninitialized_experiment_cli_representation(experiment: Experiment):
    return UninitializedExperimentCliModel(name=experiment.name, parameters_spec=' '.join(experiment.parameters_spec),
                                           metrics='', start_date='', end_date='', duration='',
                                           creation_timestamp=format_timestamp_for_cli(experiment.creation_timestamp),
                                           submitter=experiment.namespace, status=experiment.state.value,
                                           template_name=experiment.template_name,
                                           template_version=experiment.template_version)


def list_unitialized_experiments_in_cli(verbosity_lvl: int, all_users: bool,
                                        name: str, headers: List[str], listed_runs_kinds: List[RunKinds] = None,
                                        count: int = None, brief: bool = False):
    """
    Display a list of selected runs in the cli.

    :param verbosity_lvl: level at which error messages should be logged or displayed
    :param all_users: whether to display runs regardless of their owner or not
    :param name: regular expression to which names of the shown runs have to match
    :param headers: headers which will be displayed on top of a table shown in the cli
    :param count: number of rows displayed on a list. If not given - content of a list is not limited
    """

    if not listed_runs_kinds:
        listed_runs_kinds = [RunKinds.TRAINING, RunKinds.JUPYTER]

    try:
        namespace = None if all_users else get_kubectl_current_context_namespace()

        creating_experiments = Experiment.list(namespace=namespace,
                                               state=ExperimentStatus.CREATING,
                                               run_kinds_filter=listed_runs_kinds,
                                               name_filter=name)
        runs = Run.list(namespace=namespace, name_filter=name, run_kinds_filter=listed_runs_kinds)

        # Get Experiments without associated Runs
        names_of_experiment_with_runs = set()
        for run in runs:
            names_of_experiment_with_runs.add(run.experiment_name)

        uninitialized_experiments = [experiment for experiment in creating_experiments
                                     if experiment.name not in names_of_experiment_with_runs]

        displayed_items_count = count if count else len(uninitialized_experiments)
        click.echo(tabulate([uninitialized_experiment_cli_representation(experiment)
                             for experiment in uninitialized_experiments][-displayed_items_count:],
                            headers=headers, tablefmt="orgtbl"))
    except InvalidRegularExpressionError:
        handle_error(logger, Texts.INVALID_REGEX_ERROR_MSG, Texts.INVALID_REGEX_ERROR_MSG,
                     add_verbosity_msg=verbosity_lvl == 0)
        exit(1)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=verbosity_lvl == 0)
        exit(1)


def list_runs_in_cli(verbosity_lvl: int, all_users: bool, name: str,
                     listed_runs_kinds: List[RunKinds], runs_list_headers: List[str], with_metrics: bool,
                     status: RunStatus = None, count: int = None, brief: bool = False):
    """
    Display a list of selected runs in the cli.

    :param verbosity_lvl: level at which error messages should be logged or displayed
    :param all_users: whether to display runs regardless of their owner or not
    :param name: regular expression to which names of the shown runs have to match
    :param status: display runs with this status
    :param listed_runs_kinds: list of kinds of runs that will be listed out
    :param runs_list_headers: headers which will be displayed on top of a table shown in the cli
    :param with_metrics: whether to show metrics column or not
    :param count: number of rows displayed on a list. If not given - content of a list is not limited
    :param brief: when true only experiment name, submission date, owner and state will be print
    """

    try:
        namespace = None if all_users else get_kubectl_current_context_namespace()

        # List experiments command is actually listing Run resources instead of Experiment resources with one
        # exception - if run is initialized - dlsctl displays data of an experiment instead of data of a run
        runs = replace_initializing_runs(
            Run.list(namespace=namespace, state_list=[status], name_filter=name, run_kinds_filter=listed_runs_kinds))

        runs_representations = [run.cli_representation for run in runs]
        if brief:
            runs_table_data = [
                (run_representation.name, run_representation.submission_date, run_representation.submitter,
                 run_representation.status)
                for run_representation in runs_representations
            ]
        elif with_metrics:
            runs_table_data = runs_representations
        else:
            runs_table_data = [
                (run_representation.name, run_representation.parameters,  # type: ignore
                 run_representation.submission_date,
                 run_representation.start_date, run_representation.duration,
                 run_representation.submitter, run_representation.status, run_representation.template_name,
                 run_representation.template_version)
                for run_representation in runs_representations
            ]
        click.echo(tabulate(runs_table_data if not count else runs_table_data[-count:],
                            headers=runs_list_headers, tablefmt="orgtbl"))
    except InvalidRegularExpressionError:
        handle_error(logger, Texts.INVALID_REGEX_ERROR_MSG, Texts.INVALID_REGEX_ERROR_MSG,
                     add_verbosity_msg=verbosity_lvl == 0)
        exit(1)
    except Exception:
        handle_error(logger, Texts.OTHER_ERROR_MSG, Texts.OTHER_ERROR_MSG, add_verbosity_msg=verbosity_lvl == 0)
        exit(1)


def replace_initializing_runs(run_list: List[Run]):
    """
    Creates a list of runs with initializing runs replaced by fake runs created based
    on experiment data. If there is at least one initializing run within a certain
    experiment - none of runs creating this experiment is displayed.
    :param run_list: list of runs to be checked
    :return: list without runs that are initialized at the moment
    """
    initializing_experiments: set = set()
    ret_list = []
    for run in run_list:
        exp_name = run.experiment_name
        experiment = Experiment.get(name=exp_name, namespace=run.namespace)
        if (run.state is None or run.state == '') and exp_name not in initializing_experiments:
            ret_list.append(create_fake_run(experiment))
            initializing_experiments.add(exp_name)
        elif exp_name not in initializing_experiments:
            if experiment:
                run.template_version = experiment.template_version
            else:
                run.template_version = None
            ret_list.append(run)

    return ret_list


def create_fake_run(experiment: Experiment) -> Run:
    return Run(name=experiment.name, experiment_name=experiment.name, metrics={},
               parameters=experiment.parameters_spec, pod_count=0,
               pod_selector={}, state=RunStatus.CREATING, namespace=experiment.namespace,
               creation_timestamp=experiment.creation_timestamp,
               template_name=experiment.template_name,
               template_version=experiment.template_version)


def get_logs(experiment_name: str, min_severity: SeverityLevel, start_date: str,
             end_date: str, pod_ids: str, pod_status: PodStatus, match: str, output: bool,
             pager: bool, follow: bool, runs_kinds: List[RunKinds], instance_type: str):
    """
    Show logs for a given experiment.
    """
    # check whether we have runs with a given name
    if experiment_name and match:
        handle_error(user_msg=Texts.NAME_M_BOTH_GIVEN_ERROR_MSG.format(instance_type=instance_type))
        exit(1)
    elif not experiment_name and not match:
        handle_error(user_msg=Texts.NAME_M_NONE_GIVEN_ERROR_MSG.format(instance_type=instance_type))
        exit(1)

    try:
        with K8sProxy(NAUTAAppNames.ELASTICSEARCH) as proxy:
            es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                               verify_certs=False, use_ssl=False)
            namespace = get_kubectl_current_context_namespace()
            if match:
                experiment_name = match
                name_filter = match
            else:
                name_filter = f'^{experiment_name}$'
            runs = Run.list(namespace=namespace, name_filter=name_filter, run_kinds_filter=runs_kinds)
            if not runs:
                raise ValueError(f'Run with given name: {experiment_name} does not exists in namespace {namespace}.')

            pod_ids = pod_ids.split(',') if pod_ids else None  # type: ignore
            follow_logs = True if follow and not output else False

            if output and len(runs) > 1:
                click.echo(Texts.MORE_EXP_LOGS_MESSAGE)

            for run in runs:
                start_date = start_date if start_date else run.creation_timestamp

                run_logs_generator = es_client.get_experiment_logs_generator(run=run, namespace=namespace,
                                                                             min_severity=min_severity,
                                                                             start_date=start_date, end_date=end_date,
                                                                             pod_ids=pod_ids, pod_status=pod_status,
                                                                             follow=follow_logs)

                if output:
                    save_logs_to_file(run=run, run_logs_generator=run_logs_generator, instance_type=instance_type)
                else:
                    if len(runs) > 1:
                        click.echo(f'Experiment : {run.name}')
                    print_logs(run_logs_generator=run_logs_generator, pager=pager)

    except K8sProxyCloseError:
        handle_error(logger, Texts.PROXY_CLOSE_LOG_ERROR_MSG, Texts.PROXY_CLOSE_USER_ERROR_MSG)
        exit(1)
    except LocalPortOccupiedError as exe:
        handle_error(logger, Texts.LOCAL_PORT_OCCUPIED_ERROR_MSG.format(exception_message=exe.message),
                     Texts.LOCAL_PORT_OCCUPIED_ERROR_MSG.format(exception_message=exe.message))
        exit(1)
    except K8sProxyOpenError:
        handle_error(logger, Texts.PROXY_CREATION_ERROR_MSG, Texts.PROXY_CREATION_ERROR_MSG)
        exit(1)
    except ValueError:
        handle_error(logger, Texts.EXPERIMENT_NOT_EXISTS_ERROR_MSG.format(experiment_name=experiment_name,
                                                                          instance_type=instance_type.capitalize()),
                     Texts.EXPERIMENT_NOT_EXISTS_ERROR_MSG.format(experiment_name=experiment_name,
                                                                  instance_type=instance_type.capitalize()))
        exit(1)
    except Exception:
        handle_error(logger, Texts.LOGS_GET_OTHER_ERROR_MSG.format(instance_type=instance_type),
                     Texts.LOGS_GET_OTHER_ERROR_MSG.format(instance_type=instance_type))
        exit(1)


def format_log_date(date: str):
    log_date = dateutil.parser.parse(date)
    log_date = log_date.replace(microsecond=0)
    formatted_date = log_date.isoformat()
    return formatted_date


def print_logs(run_logs_generator: Generator[LogEntry, None, None], pager=False):
    def formatted_logs():
        for log_entry in run_logs_generator:
            if not log_entry.content.isspace():
                formatted_date = format_log_date(log_entry.date)
                yield f'{formatted_date} {log_entry.pod_name} {log_entry.content}'

    if pager:
        # set -K option for less, so ^C will be respected
        os.environ['LESS'] = os.environ.get('LESS', '') + ' -K'
        click.echo_via_pager(formatted_logs)  # type: ignore
    else:
        for formatted_log in formatted_logs():
            click.echo(formatted_log, nl=False)


def save_logs_to_file(run: Run, run_logs_generator: Generator[LogEntry, None, None], instance_type: str):
    filename = run.name + '.log'
    confirmation_message = Texts.LOGS_STORING_CONFIRMATION.format(filename=filename,
                                                                  experiment_name=run.name,
                                                                  instance_type=instance_type)
    if os.path.isfile(filename):
        confirmation_message = Texts.LOGS_STORING_CONFIRMATION_FILE_EXISTS.format(filename=filename,
                                                                                  experiment_name=run.name,
                                                                                  instance_type=instance_type)

    if click.confirm(confirmation_message, default=True):
        try:
            with open(filename, 'w') as file, spinner(spinner=NctlSpinner,
                                                      text=Texts.SAVING_LOGS_TO_FILE_PROGRESS_MSG, color=SPINNER_COLOR):
                for log_entry in run_logs_generator:
                    if not log_entry.content.isspace():
                        formatted_date = format_log_date(log_entry.date)
                        file.write(f'{formatted_date} {log_entry.pod_name} {log_entry.content}')
            click.echo(Texts.LOGS_STORING_FINAL_MESSAGE)
        except Exception as exe:
            handle_error(logger,
                         Texts.LOGS_STORING_ERROR,
                         Texts.LOGS_STORING_ERROR)
            exit(1)
    else:
        click.echo(Texts.LOGS_STORING_CANCEL_MESSAGE)
