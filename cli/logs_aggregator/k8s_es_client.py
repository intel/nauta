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
from typing import List

import elasticsearch

from logs_aggregator.log_filters import SeverityLevel, filter_logs_by_severity,\
    filter_logs_by_pod_status
from logs_aggregator.k8s_log_entry import LogEntry
from util.logger import initialize_logger
from util.k8s_info import PodStatus


log = initialize_logger(__name__)

ELASTICSEARCH_K8S_SERVICE = 'elasticsearch-svc'


class K8sElasticSearchClient(elasticsearch.Elasticsearch):
    def __init__(self, host: str, port: int, namespace: str, use_ssl=True, verify_certs=True, **kwargs):
        hosts = [{'host': host,
                  'url_prefix': f'api/v1/namespaces/{namespace}/services/{ELASTICSEARCH_K8S_SERVICE}/proxy',
                  'port': port}]
        super().__init__(hosts=hosts, use_ssl=use_ssl, verify_certs=verify_certs, **kwargs)

    def get_pod_logs(self, pod_name: str, index='_all',
                     start_date: str = None, end_date: str = None,
                     log_count=100, sort='@timestamp:asc') -> List[LogEntry]:
        """
        Return logs for given pod.
        :param pod_name: Name of pod to search
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param start_date: if provided, only logs produced after this date will be returned
        :param end_date: if provided, only logs produced before this date will be returned
        :param log_count: Number of log entries that will be returned
        :param sort: Sorting command in field:direction format
        :return: List of LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        log.debug(f'Searching for {pod_name} pod logs.')

        if start_date or end_date:
            start_date = start_date or '*'
            end_date = end_date or '*'
            lucene_query = f'kubernetes.pod_name:"{pod_name}" AND @timestamp:[{start_date} TO {end_date}]'
        else:
            lucene_query = f'kubernetes.pod_name:"{pod_name}"'

        found_logs = self.search(q=lucene_query,
                                 index=index, size=log_count, sort=sort)
        pod_logs = [LogEntry(date=hit['_source']['@timestamp'],
                             content=hit['_source']['log'],
                             pod_name=hit['_source']['kubernetes']['pod_name'],
                             namespace=hit['_source']['kubernetes']['namespace_name'])
                    for hit in found_logs['hits']['hits']]

        log.debug(f'Logs found for {pod_name} pod: {pod_logs}')
        return pod_logs

    def get_experiment_logs(self, experiment_name: str, min_severity: SeverityLevel or str = None,
                            log_count=100, start_date: str = None, end_date: str = None,
                            pod_ids: List[str] = None, pod_status: PodStatus = None) -> List[LogEntry]:
        """
        Return logs for given experiment. Currently, experiment corresponds to a single k8s pod.
        :param experiment_name: Name of experiment.
        :param severity: pass optional minimal severity level for logs to be retrieved,
         if set to None, all logs will be returned
        :param log_count: number of log entries to be returned
        :param start_date: string representing a initial date for logs that will be returned
        :param end_date: string representing a final date for logs that will be returned
        :param pod_ids: If provided, only logs from pods with given IDs will be returned
        :return: List of LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        if pod_ids:
            pod_logs = [log for pod_id in pod_ids for log
                        in self.get_pod_logs(pod_name=pod_id, log_count=log_count,
                                             start_date=start_date, end_date=end_date)]
            pod_logs.sort(key=lambda log_entry: dateutil.parser.parse(log_entry.date))
        else:
            pod_logs = self.get_pod_logs(pod_name=experiment_name, log_count=log_count,
                                         start_date=start_date, end_date=end_date)

        if min_severity:
            pod_logs = filter_logs_by_severity(logs=pod_logs, min_severity=min_severity)
        if pod_status:
            pod_logs = filter_logs_by_pod_status(logs=pod_logs, pod_status=pod_status)

        return pod_logs
