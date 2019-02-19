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

from functools import partial
import time
from typing import List, Callable, Generator

import elasticsearch
import elasticsearch.helpers
import elasticsearch.client

from logs_aggregator.log_filters import SeverityLevel, filter_log_by_severity, \
    filter_log_by_pod_status, filter_log_by_pod_ids
from logs_aggregator.k8s_log_entry import LogEntry
from platform_resources.platform_resource import PlatformResource
from platform_resources.workflow import ArgoWorkflow
from util.logger import initialize_logger
from util.k8s.k8s_info import PodStatus
from platform_resources.run import Run

logger = initialize_logger(__name__)

ELASTICSEARCH_K8S_SERVICE = 'elasticsearch-svc'


class K8sElasticSearchClient(elasticsearch.Elasticsearch):
    def __init__(self, host: str, port: int,
                 use_ssl=True, verify_certs=True, **kwargs):
        hosts = [{'host': host,
                  'port': port}]
        super().__init__(hosts=hosts, use_ssl=use_ssl, verify_certs=verify_certs, **kwargs)

    def get_log_generator(self, query_body: dict = None, index='_all', scroll='1m',
                          filters: List[Callable[[LogEntry], bool]] = None) -> Generator[LogEntry, None, None]:
        """
        A generator that yields LogEntry objects constructed from Kubernetes resource logs.
        Logs to be returned are defined by passed query and filtered according to passed
        filter functions, which have to accept LogEntry as argument and return a boolean value.
        :param query_body: ES search query
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param scroll: ElasticSearch scroll lifetime
        :param filters: List of filter functions with signatures f(LogEntry) -> Bool
        :return: Generator yielding LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        for log in elasticsearch.helpers.scan(self, query=query_body, index=index, scroll=scroll, size=1000,
                                              preserve_order=True, clear_scroll=False):
            log_entry = LogEntry(date=log['_source']['@timestamp'],
                                 content=log['_source']['log'],
                                 pod_name=log['_source']['kubernetes']['pod_name'],
                                 namespace=log['_source']['kubernetes']['namespace_name'])
            if not filters or all(f(log_entry) for f in filters):
                yield log_entry

    def get_stream_log_generator(self, query_body: dict = None, index='_all', scroll='1m', time_interval=0.5,
                                 filters: List[Callable[[LogEntry], bool]] = None) -> Generator[LogEntry, None, None]:
        """
        A generator that yields LogEntry objects constructed from Kubernetes resource logs.
        Logs to be returned are defined by passed query and filtered according to passed
        filter functions, which have to accept LogEntry as argument and return a boolean value.
        Generator will always try to obtain new log entries, whenever it will be iterated over.
        :param query_body: ES search query
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param scroll: ElasticSearch scroll lifetime
        :param time_interval: Time interval between attempting to get a new batch of logs
        :param filters: List of filter functions with signatures f(LogEntry) -> Bool
        :return: Generator yielding LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        last_timestamp = None
        while True:
            for log in self.get_log_generator(query_body=query_body, index=index, scroll=scroll, filters=filters):
                last_timestamp = log.date
                yield log
            else:
                # Scan is exhausted - try to fetch a new batch of logs
                # Note that we expect specific query structure here
                if last_timestamp:
                    query_body['query']['bool']['filter']['range']['@timestamp']['gt'] = last_timestamp
                time.sleep(time_interval)

    def get_experiment_logs_generator(self, run: Run, namespace: str, start_date: str, end_date: str = None,
                                      index='_all', pod_ids: List[str] = None, pod_status: PodStatus = None,
                                      min_severity: SeverityLevel = None, follow=False) -> Generator[LogEntry, None, None]:
        """
        Return logs for given experiment (interpreted as Run object).
        :param run: instance of Run resource
        :param namespace: Name of namespace where experiment was started
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param start_date: if provided, only logs produced after this date will be returned
        :param end_date: if provided, only logs produced before this date will be returned
        :param pod_ids: filter logs by pod ids
        :param pod_status: filter logs by pod status
        :param min_severity: yield logs with minimum provided severity
        :param follow: if True, generator will stream logs tail
        :return: Generator yielding LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        logger.debug(f'Searching for {run.name} Run logs.')

        timestamp_range_filter = {"range": {"@timestamp": {"gte": start_date}}}
        if end_date:
            timestamp_range_filter = {"range": {"@timestamp":{"gte": start_date, "lte": end_date}}}

        filters = []
        if min_severity:
            filters.append(partial(filter_log_by_severity, min_severity=min_severity))
        if pod_status:
            filters.append(partial(filter_log_by_pod_status, pod_status=pod_status))
        if pod_ids:
            filters.append(partial(filter_log_by_pod_ids, pod_ids=set(pod_ids)))


        log_generator = self.get_stream_log_generator if follow else self.get_log_generator

        experiment_logs_generator = log_generator(query_body={
            "query": {"bool": {"must":
                                   [{'term': {'kubernetes.labels.runName.keyword': run.name}},
                                    {'term': {'kubernetes.namespace_name.keyword': namespace}}
                                    ],
                               "filter": timestamp_range_filter
                               }},
            "sort": {"@timestamp": {"order": "asc"}}},
            index=index, filters=filters)

        return experiment_logs_generator

    def get_argo_workflow_logs_generator(self, workflow: ArgoWorkflow, namespace: str,
                                         start_date: str, end_date: str = None,
                                         index='_all', follow=False):
        """
        Return logs for given Argo workflow
        :param workflow: instance of ArgoWorkflow resource
        :param namespace: Name of namespace where experiment was started
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        :param start_date: if provided, only logs produced after this date will be returned
        :param end_date: if provided, only logs produced before this date will be returned
        :param follow: if True, generator will stream logs tail
        :return: Generator yielding LogEntry (date, log_content, pod_name, namespace) named tuples.
        """
        logger.debug(f'Searching for {workflow.name} workflow logs.')

        timestamp_range_filter = {"range": {"@timestamp": {"gte": start_date}}}
        if end_date:
            timestamp_range_filter = {"range": {"@timestamp": {"gte": start_date, "lte": end_date}}}

        filters = []

        log_generator = self.get_stream_log_generator if follow else self.get_log_generator

        workflow_logs_generator = log_generator(query_body={
            "query": {"bool": {"must":
                                   [{'term':
                                         {'kubernetes.labels.workflows_argoproj_io/workflow.keyword': workflow.name}},
                                    {'term': {'kubernetes.namespace_name.keyword': namespace}}
                                    ],
                               "filter": timestamp_range_filter
                               }},
            "sort": {"@timestamp": {"order": "asc"}}},
            index=index, filters=filters)

        return workflow_logs_generator

    def delete_logs_for_namespace(self, namespace: str, index='_all'):
        """
        Removes logs for a given namespace.
        :param namespace: namespace for which logs should be deleted
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        Throws exception in case of any errors during removing of logs.
        """
        logger.debug(f'Deleting logs for {namespace} namespace.')

        delete_query = {"query": {"term": {'kubernetes.namespace_name.keyword': namespace}}}
        output = self.delete_by_query(index=index, body=delete_query)

        logger.debug(f"Deleting logs - result: {str(output)}")

    def delete_logs_for_run(self, run: str, namespace: str, index='_all'):
        """
        Removes logs for a given run.
        :param run: run for which logs should be deleted
        :param namespace: namespace for which logs should be deleted
        :param index: ElasticSearch index from which logs will be retrieved, defaults to all indices
        Throws exception in case of any errors during removing of logs.
        """
        logger.debug(f'Deleting logs for {run} run and namespace {namespace}.')

        delete_query = {"query": {"bool": {"must":
            [
                {"term": {'kubernetes.labels.runName.keyword': run}},
                {"term": {'kubernetes.namespace_name.keyword': namespace}}
            ]
        }
        }
        }

        output = self.delete_by_query(index=index, body=delete_query)

        logger.debug(f"Deleting logs - result: {str(output)}")
