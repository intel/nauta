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
from util.k8s_info import get_kubectl_host, get_kubectl_port, PodStatus

@click.command()
@click.argument('experiment-name')
@click.option('--namespace', default='kube-system', help='Namespace where ElasticSearch k8s service is deployed')
@click.option('--min-severity', type=click.Choice([level.name for level in SeverityLevel]),
              help='Minimal severity of logs')
@click.option('--start-date', default=None, help='Retrieve logs produced from this date (use ISO 8601 date format)')
@click.option('--end-date', default=None, help='Retrieve logs produced until this date (use ISO 8601 date format)')
@click.option('--pod-ids', default=None, help='Comma separated list of pod IDs, if provided, only logs from these '
                                              'pods will be returned')
@click.option('--pod-status', default=None, type=click.Choice([status.name for status in PodStatus]),
              help='Get logs only for pods with given status')
def logs(experiment_name: str, namespace: str, min_severity: SeverityLevel, start_date: str,
         end_date: str, pod_ids: str, pod_status: PodStatus):
    """
    Show logs for given experiment.
    """

    # Namespace option is used temporary until we will have namespace written in configuration file
    es_client = K8sElasticSearchClient(host=get_kubectl_host(), port=get_kubectl_port(),
                                       namespace=namespace, verify_certs=False)

    pod_ids = pod_ids.split(',') if pod_ids else None
    min_severity = SeverityLevel(min_severity) if min_severity else None
    pod_status = PodStatus(pod_status) if pod_status else None
    experiment_logs = es_client.get_experiment_logs(experiment_name=experiment_name, min_severity=min_severity,
                                                    start_date=start_date, end_date=end_date, pod_ids=pod_ids,
                                                    pod_status=pod_status)
    experiment_logs = ''.join([f'{log_entry.date} {log_entry.pod_name} {log_entry.content}' for log_entry
                               in experiment_logs if not log_entry.content.isspace()])
    click.echo(experiment_logs)
