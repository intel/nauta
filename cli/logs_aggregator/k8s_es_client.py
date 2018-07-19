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
from functools import partial
from typing import List, Callable, Generator

import elasticsearch
import elasticsearch.helpers
import elasticsearch.client

from logs_aggregator.log_filters import SeverityLevel, filter_log_by_severity,\
    filter_log_by_pod_status, filter_log_by_pod_ids
from logs_aggregator.k8s_log_entry import LogEntry
from util.logger import initialize_logger
from util.k8s.k8s_info import PodStatus
from platform_resources.run_model import Run


log = initialize_logger(__name__)

ELASTICSEARCH_K8S_SERVICE = 'elasticsearch-svc'


class K8sElasticSearchClient(elasticsearch.Elasticsearch):
    def __init__(self, host: str, port: int,
                 use_ssl=True, verify_certs=True, **kwargs):
        hosts = [{'host': host,
                  'port': port}]
        super().__init__(hosts=hosts, use_ssl=use_ssl, verify_certs=verify_certs, **kwargs)

    def full_log_search(self, lucene_query: str = None, index='_all',
                        scroll='1m', filters: List[Callable] = None) -> Generator[LogEntry, None, None]:
        """
        A generator that yields LogEntry objects constructed from Kubernetes resource logs.
        Logs to be returned are defined by passed Lucene query and filtered according to passed
        filter functions, which have to accept LogEntry as argument and return a boolean value.
        :param lucene_query: Lucene query string
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param scroll: ElasticSearch scroll lifetime
        :param filters: List of filter functions with signatures f(LogEntry) -> Bool
        :return:
        """
        for log in elasticsearch.helpers.scan(self, q=lucene_query, index=index, scroll=scroll, clear_scroll=False):
            log_entry = LogEntry(date=log['_source']['@timestamp'],
                                 content=log['_source']['log'],
                                 pod_name=log['_source']['kubernetes']['pod_name'],
                                 namespace=log['_source']['kubernetes']['namespace_name'])
            if not filters or all(f(log_entry) for f in filters):
                yield log_entry

    def get_experiment_logs(self, run: Run, namespace: str, index='_all',
                            start_date: str = None, end_date: str = None,
                            pod_ids: List[str] = None, pod_status: PodStatus = None,
                            min_severity: SeverityLevel = None) -> List[LogEntry]:
        """
        Return logs for given experiment.
        :param run: instance of Run resource
        :param namespace: Name of namespace where experiment was started
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param start_date: if provided, only logs produced after this date will be returned
        :param end_date: if provided, only logs produced before this date will be returned
        :param pod_ids: filter logs by pod ids
        :param pod_status: filter logs by pod status
        :param min_severity: return logs with minimum provided severity
        :return: List of LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        log.debug(f'Searching for {run.name} Run logs.')

        lucene_query = f'kubernetes.labels.runName.keyword:\"{run.name}\" ' \
                       f'AND kubernetes.namespace_name.keyword:\"{namespace}\"'

        if start_date or end_date:
            start_date = start_date or '*'
            end_date = end_date or '*'
            lucene_query += f' AND @timestamp:[{start_date} TO {end_date}]'

        filters = []
        if min_severity:
            filters.append(partial(filter_log_by_severity, min_severity=min_severity))
        if pod_status:
            filters.append(partial(filter_log_by_pod_status, pod_status=pod_status))
        if pod_ids:
            filters.append(partial(filter_log_by_pod_ids, pod_ids=set(pod_ids)))

        experiment_logs = sorted(self.full_log_search(lucene_query=lucene_query, index=index, filters=filters),
                                 key=lambda log_entry: dateutil.parser.parse(log_entry.date))

        if experiment_logs:
            log.debug(f'Logs found for Run {run.name}.')
        else:
            log.debug(f'Logs not found for Run {run.name}.')
        return experiment_logs

    def delete_logs_for_namespace(self, namespace: str, index='_all'):
        """
        Removes logs for a given namespace.
        :param namespace: namespace for which logs should be deleted
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        Throws exception in case of any errors during removing of logs.
        """
        log.debug(f'Deleting logs for {namespace} namespace.')

        delete_query = {"query": {"term": {'kubernetes.namespace_name.keyword': namespace}}}
        output = self.delete_by_query(index=index, body=delete_query)

        log.debug(f"Deleting logs - result: {str(output)}")


    def delete_logs_for_run(self, run: str, index='_all'):
        """
        Removes logs for a given run.
        :param run: run for which logs should be deleted
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        Throws exception in case of any errors during removing of logs.
        """
        log.debug(f'Deleting logs for {run} run.')

        delete_query = {"query": {"term": {'kubernetes.labels.runName.keyword': run}}}
        output = self.delete_by_query(index=index, body=delete_query)

        log.debug(f"Deleting logs - result: {str(output)}")