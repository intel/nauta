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

import click

from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.log_filters import SeverityLevel
from platform_resources.runs import get_run
from cli_state import common_options, pass_state, State
from util.k8s.k8s_info import PodStatus, get_kubectl_current_context_namespace
from util.logger import initialize_logger
from util.app_names import DLS4EAppNames

from util.aliascmd import AliasCmd
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.k8s.k8s_proxy_context_manager import K8sProxy


logger = initialize_logger(__name__)


@click.command(cls=AliasCmd, alias='lg')
@click.argument('experiment-name')
@click.option('-s', '--min-severity', type=click.Choice([level.name for level in SeverityLevel]),
              help='Show all events with this specified minimal and greater severity.')
@click.option('-sd', '--start-date', default=None,
              help='Retrieve all logs produced on and after this date (use ISO 8601 date format).')
@click.option('-ed', '--end-date', default=None,
              help='Retrieve all logs produced on and before this date (use ISO 8601 date format).')
@click.option('-i', '--pod-ids', default=None,
              help='Comma separated list of pod IDs. If provided, only logs from these pods will be returned.')
@click.option('-p', '--pod-status', default=None, type=click.Choice([status.name for status in PodStatus]),
              help='Get logs only for pods with given status.')
@common_options()
@pass_state
def logs(state: State, experiment_name: str, min_severity: SeverityLevel, start_date: str,
         end_date: str, pod_ids: str, pod_status: PodStatus):
    """
    Show logs for a given experiment.
    """
    try:
        with K8sProxy(DLS4EAppNames.ELASTICSEARCH) as proxy:
            es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                               verify_certs=False, use_ssl=False)
            namespace = get_kubectl_current_context_namespace()
            run = get_run(name=experiment_name, namespace=namespace)
            if not run:
                raise ValueError(f'Run with given name: {experiment_name} does not exists in namespace {namespace}.')

            pod_ids = pod_ids.split(',') if pod_ids else None
            min_severity = SeverityLevel[min_severity] if min_severity else None
            pod_status = PodStatus[pod_status] if pod_status else None

            experiment_logs = es_client.get_experiment_logs(run=run,
                                                            namespace=namespace,
                                                            min_severity=min_severity,
                                                            start_date=start_date, end_date=end_date, pod_ids=pod_ids,
                                                            pod_status=pod_status)
            experiment_logs = ''.join([f'{log_entry.date} {log_entry.pod_name} {log_entry.content}' for log_entry
                                       in experiment_logs if not log_entry.content.isspace()])
            click.echo(experiment_logs)
    except K8sProxyCloseError:
        logger.exception("Error during closing of a proxy for elasticsearch.")
        sys.exit("Elasticsearch proxy hasn't been closed properly. "
                 "Check whether it still exists, if yes - close it manually.")
    except LocalPortOccupiedError as exe:
        msg = f"Error during creation of a proxy for elasticsearch. {exe.message}"
        logger.exception(msg)
        sys.exit(msg)
    except K8sProxyOpenError:
        msg = "Error during creation of a proxy for elasticsearch."
        logger.exception(msg)
        sys.exit(msg)
    except ValueError:
        msg = f"Experiment with name {experiment_name} does not exist."
        logger.exception(msg)
        sys.exit(msg)
    except Exception:
        error_msg = 'Failed to get experiment logs.'
        logger.exception(error_msg)
        sys.exit(error_msg)
