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


import os
from sys import exit
from typing import List, Generator

import click
import dateutil.parser

from cli_text_consts import CmdsCommonTexts as Texts, SPINNER_COLOR
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.k8s_log_entry import LogEntry
from logs_aggregator.log_filters import SeverityLevel
from platform_resources.run import RunKinds, Run
from util.k8s.k8s_info import PodStatus, get_kubectl_host, get_api_key, get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.spinner import spinner, NctlSpinner
from util.system import handle_error

logger = initialize_logger(__name__)


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
        es_client = K8sElasticSearchClient(host=f'{get_kubectl_host(with_port=True)}'
                                           f'/api/v1/namespaces/nauta/services/nauta-elasticsearch:nauta/proxy',
                                           verify_certs=False, use_ssl=True,
                                           headers={'Authorization': get_api_key()})
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
                save_logs_to_file(logs_generator=run_logs_generator, instance_name=run.name,
                                  instance_type=instance_type)
            else:
                if len(runs) > 1:
                    click.echo(f'Experiment : {run.name}')
                print_logs(run_logs_generator=run_logs_generator, pager=pager)
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


def save_logs_to_file(logs_generator: Generator[LogEntry, None, None], instance_name: str,
                      instance_type: str):
    filename = instance_name + ".log"
    confirmation_message = Texts.LOGS_STORING_CONF.format(filename=filename,
                                                          instance_name=instance_name,
                                                          instance_type=instance_type)
    if os.path.isfile(filename):
        confirmation_message = Texts.LOGS_STORING_CONF_FILE_EXISTS.format(filename=filename,
                                                                          instance_name=instance_name,
                                                                          instance_type=instance_type)

    if click.get_current_context().obj.force or click.confirm(confirmation_message, default=True):
        try:
            with open(filename, 'w') as file, spinner(spinner=NctlSpinner,
                                                      text=Texts.SAVING_LOGS_TO_FILE_PROGRESS_MSG, color=SPINNER_COLOR):
                for log_entry in logs_generator:
                    if not log_entry.content.isspace():
                        formatted_date = format_log_date(log_entry.date)
                        file.write(f'{formatted_date} {log_entry.pod_name} {log_entry.content}')
            click.echo(Texts.LOGS_STORING_FINAL_MESSAGE)
        except Exception:
            handle_error(logger,
                         Texts.LOGS_STORING_ERROR,
                         Texts.LOGS_STORING_ERROR)
            exit(1)
    else:
        click.echo(Texts.LOGS_STORING_CANCEL_MESSAGE)
