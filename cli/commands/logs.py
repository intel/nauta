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
from util.k8s_info import get_kubectl_host, get_kubectl_port

@click.command()
@click.argument('experiment-name')
@click.option('--namespace', default='kube-system')
def logs(experiment_name: str, namespace: str):
    """
    Show logs for given experiment.
    """

    # Namespace option is temporary until we will have namespace written in configuration file
    es_client = K8sElasticSearchClient(host=get_kubectl_host(), port=get_kubectl_port(),
                                       namespace=namespace, verify_certs=False)
    experiment_logs = es_client.get_experiment_logs(experiment_name=experiment_name)
    experiment_logs = ''.join([f'{timestamp} {log_content}' for timestamp, log_content
                               in experiment_logs if not log_content.isspace()])
    click.echo(experiment_logs)
