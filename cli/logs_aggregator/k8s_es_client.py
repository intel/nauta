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

from typing import List, Tuple

from elasticsearch import Elasticsearch

from util.logger import initialize_logger


log = initialize_logger(__name__)


ELASTICSEARCH_K8S_SERVICE = 'elasticsearch-svc'

class K8sElasticSearchClient(Elasticsearch):
    def __init__(self, host: str, port: int, namespace: str, use_ssl=True, verify_certs=True, **kwargs):
        hosts = [{'host': host,
                  'url_prefix': f'api/v1/namespaces/{namespace}/services/{ELASTICSEARCH_K8S_SERVICE}/proxy',
                  'port': port}]
        super().__init__(hosts=hosts, use_ssl=use_ssl, verify_certs=verify_certs, **kwargs)

    def get_pod_logs(self, pod_name: str, index='_all',
                     log_count=100, sort='@timestamp:asc') -> List[Tuple[str, str]]:
        """
        Return logs for given pod.
        :param pod_name: Name of pod
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param log_count: Number of log entries that will be returned
        :param sort: Sorting command in field:direction format
        :return: List of (timestamp, log_content) tuples.
        """
        log.debug(f'Searching for {pod_name} pod logs.')
        found_logs = self.search(q=f'kubernetes.pod_name:{pod_name}',
                                 index=index, size=log_count, sort=sort)
        pod_logs = [(hit['_source']['@timestamp'], hit['_source']['log'])
                    for hit in found_logs['hits']['hits']]

        log.debug(f'Logs found for {pod_name} pod: {pod_logs}')
        return pod_logs

    def get_experiment_logs(self, experiment_name: str) -> List[Tuple[str, str]]:
        """
        Return logs for given experiment. Currently, experiment corresponds to a single k8s pod.
        :param experiment_name: Name of experiment.
        :return: List of (timestamp, log_content) tuples.
        """
        return self.get_pod_logs(pod_name=experiment_name)
