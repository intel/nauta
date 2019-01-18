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

import dateutil.parser
import os.path
from sys import exit
from typing import Generator

import click

from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.k8s_log_entry import LogEntry
from logs_aggregator.log_filters import SeverityLevel
from platform_resources.run_model import Run
from platform_resources.runs import list_runs
from cli_state import common_options, pass_state, State
from util.k8s.k8s_info import PodStatus, get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.app_names import NAUTAAppNames
from util.aliascmd import AliasCmd
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.spinner import spinner, NctlSpinner
from util.system import handle_error
from cli_text_consts import ExperimentLogsCmdTexts as Texts, SPINNER_COLOR

logger = initialize_logger(__name__)


@click.command(help=Texts.HELP, short_help=Texts.SHORT_HELP, cls=AliasCmd, alias='lg', options_metavar='[options]')
@click.argument('experiment-name', required=False, metavar='[experiment_name]')
@click.option('-s', '--min-severity', type=click.Choice([level.name for level in SeverityLevel]), help=Texts.HELP_S)
@click.option('-sd', '--start-date', help=Texts.HELP_SD)
@click.option('-ed', '--end-date', help=Texts.HELP_ED)
@click.option('-i', '--pod-ids', help=Texts.HELP_I)
@click.option('-p', '--pod-status', type=click.Choice([status.name for status in PodStatus]),
              help=Texts.HELP_P)
@click.option('-m', '--match', help=Texts.HELP_M)
@click.option('-o', '--output', help=Texts.HELP_O, is_flag=True)
@click.option('-pa', '--pager', help=Texts.HELP_PAGER, is_flag=True, default=False)
@click.option('-f', '--follow', help=Texts.HELP_F, is_flag=True, default=False)
@common_options()
@pass_state
def logs(state: State, experiment_name: str, min_severity: SeverityLevel, start_date: str,
         end_date: str, pod_ids: str, pod_status: PodStatus, match: str, output: bool, pager: bool, follow: bool):
    """
    Show logs for a given experiment.
    """
    # check whether we have runs with a given name
    if experiment_name and match:
        handle_error(user_msg=Texts.NAME_M_BOTH_GIVEN_ERROR_MSG)
        exit(1)
    elif not experiment_name and not match:
        handle_error(user_msg=Texts.NAME_M_NONE_GIVEN_ERROR_MSG)
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
            runs = list_runs(namespace=namespace, name_filter=name_filter)
            if not runs:
                raise ValueError(f'Run with given name: {experiment_name} does not exists in namespace {namespace}.')

            pod_ids = pod_ids.split(',') if pod_ids else None
            min_severity = SeverityLevel[min_severity] if min_severity else None
            pod_status = PodStatus[pod_status] if pod_status else None
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
                    save_logs_to_file(run=run, run_logs_generator=run_logs_generator)
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
        handle_error(logger, Texts.EXPERIMENT_NOT_EXISTS_ERROR_MSG.format(experiment_name=experiment_name),
                     Texts.EXPERIMENT_NOT_EXISTS_ERROR_MSG.format(experiment_name=experiment_name))
        exit(1)
    except Exception:
        handle_error(logger, Texts.LOGS_GET_OTHER_ERROR_MSG, Texts.LOGS_GET_OTHER_ERROR_MSG)
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
        click.echo_via_pager(formatted_logs)
    else:
        for formatted_log in formatted_logs():
            click.echo(formatted_log, nl=False)


def save_logs_to_file(run: Run, run_logs_generator: Generator[LogEntry, None, None]):
    filename = run.name + '.log'
    confirmation_message = Texts.LOGS_STORING_CONFIRMATION.format(filename=filename,
                                                                  experiment_name=run.name)
    if os.path.isfile(filename):
        confirmation_message = Texts.LOGS_STORING_CONFIRMATION_FILE_EXISTS.format(filename=filename,
                                                                                  experiment_name=run.name)

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
                         Texts.LOGS_STORING_ERROR.format(exception_message=exe.message),
                         Texts.LOGS_STORING_ERROR.format(exception_message=exe.message))
            exit(1)
    else:
        click.echo(Texts.LOGS_STORING_CANCEL_MESSAGE)
