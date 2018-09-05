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

import click

from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.log_filters import SeverityLevel
from platform_resources.runs import list_runs
from cli_state import common_options, pass_state, State
from util.k8s.k8s_info import PodStatus, get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.app_names import DLS4EAppNames

from util.aliascmd import AliasCmd
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.system import handle_error
from cli_text_consts import EXPERIMENT_LOGS_CMD_TEXTS as TEXTS


logger = initialize_logger(__name__)


@click.command(help=TEXTS["help"], cls=AliasCmd, alias='lg')
@click.argument('experiment-name', required=False)
@click.option('-s', '--min-severity', type=click.Choice([level.name for level in SeverityLevel]), help=TEXTS["help_s"])
@click.option('-sd', '--start-date', default=None, help=TEXTS["help_sd"])
@click.option('-ed', '--end-date', default=None, help=TEXTS["help_ed"])
@click.option('-i', '--pod-ids', default=None, help=TEXTS["help_i"])
@click.option('-p', '--pod-status', default=None, type=click.Choice([status.name for status in PodStatus]),
              help=TEXTS["help_p"])
@click.option('-m', '--match', default=None, help=TEXTS["help_m"])
@common_options()
@pass_state
def logs(state: State, experiment_name: str, min_severity: SeverityLevel, start_date: str,
         end_date: str, pod_ids: str, pod_status: PodStatus, match: str):
    """
    Show logs for a given experiment.
    """
    # check whether we have runs with a given name

    if experiment_name and match:
        handle_error(user_msg=TEXTS["name_m_both_given_error_msg"])
    elif not experiment_name and not match:
        handle_error(user_msg=TEXTS["name_m_none_given_error_msg"])

    experiments_logs = {}

    try:
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH) as proxy:
            es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                               verify_certs=False, use_ssl=False)
            namespace = get_kubectl_current_context_namespace()
            if match:
                experiment_name = match
            runs = list_runs(namespace=namespace, name_filter=experiment_name)
            if not runs:
                raise ValueError(f'Run with given name: {experiment_name} does not exists in namespace {namespace}.')

            pod_ids = pod_ids.split(',') if pod_ids else None
            min_severity = SeverityLevel[min_severity] if min_severity else None
            pod_status = PodStatus[pod_status] if pod_status else None

            for run in runs:
                experiment_logs = es_client.get_experiment_logs(run=run,
                                                                namespace=namespace,
                                                                min_severity=min_severity,
                                                                start_date=start_date, end_date=end_date,
                                                                pod_ids=pod_ids,
                                                                pod_status=pod_status)
                experiment_logs = ''.join([f'{log_entry.date} {log_entry.pod_name} {log_entry.content}' for log_entry
                                           in experiment_logs if not log_entry.content.isspace()])

                experiments_logs[run.name] = experiment_logs

            if len(experiments_logs) == 1:
                click.echo(experiment_logs)
            else:
                for key, value in experiments_logs.items():
                    click.echo(f'Experiment : {key}')
                    click.echo("")
                    click.echo(value)
                    click.echo("")

    except K8sProxyCloseError:
        handle_error(logger, TEXTS["proxy_close_log_error_msg"], TEXTS["proxy_close_user_error_msg"])
    except LocalPortOccupiedError as exe:
        handle_error(logger, TEXTS["local_port_occupied_error_msg"].format(exception_message=exe.message),
                     TEXTS["local_port_occupied_error_msg"].format(exception_message=exe.message))
    except K8sProxyOpenError:
        handle_error(logger, TEXTS["proxy_creation_error_msg"], TEXTS["proxy_creation_error_msg"])
    except ValueError:
        handle_error(logger, TEXTS["experiment_not_exists_error_msg"].format(experiment_name=experiment_name),
                     TEXTS["experiment_not_exists_error_msg"].format(experiment_name=experiment_name))
    except Exception:
        handle_error(logger, TEXTS["logs_get_other_error_msg"], TEXTS["logs_get_other_error_msg"])
