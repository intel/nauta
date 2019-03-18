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

from unittest.mock import MagicMock

from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.k8s_log_entry import LogEntry
from platform_resources.run import Run
from platform_resources.workflow import ArgoWorkflow

TEST_SCAN_OUTPUT = [{'_index': 'fluentd-20180417',
                                    '_type': 'access_log',
                                    '_id': 'AWLS70tjQ4BsP2C1ykFv',
                                    '_score': None,
                                    '_source': {
                                        'log': 'Warning: Unable to load /usr/share/zoneinfo/right/Factory as time zone. Skipping it.\n',
                                        'stream': 'stdout',
                                        'docker':
                                            {'container_id': '5fdafaf3bac39f1c4dd41047df01d23ee86226556f9a255e90325e6e55fc032a'},
                                        'kubernetes':
                                            {'container_name': 'understood-gnat-mysql',
                                             'namespace_name': 'default',
                                             'pod_name': 'understood-gnat-mysql-868b556f8f-lwdr9',
                                             'pod_id': '7913bac3-4221-11e8-8f48-3e9b14d7275e',
                                             'labels': {'app': 'understood-gnat-mysql',
                                                        'pod-template-hash': '4246112949'},
                                             'host': 'minikube',
                                             'master_url': 'https://10.96.0.1:443/api',
                                             'namespace_id': '865fc7d1-02a4-11e8-9904-3e9b14d7275e'},
                                        '@timestamp': '2018-04-17T09:28:39+00:00',
                                        '@log_name': 'kubernetes.var.log.containers.understood-gnat'
                                                     '-mysql-868b556f8f-lwdr9_default_understood-gnat'
                                                     '-mysql-5fdafaf3bac39f1c4dd41047df01d23ee86226556f9a255e90325e6e55fc032a.log'}
                                       , 'sort': [1523957319000]},
                                {'_index': 'fluentd-20180417',
                                    '_type': 'access_log',
                                    '_id': 'AWLS70tjQ4BsP2C1ykFw',
                                    '_score': None,
                                    '_source':
                                        {'log': 'MySQL init process done. Ready for start up.\n',
                                         'stream': 'stdout',
                                         'docker':
                                             {'container_id': '5fdafaf3bac39f1c4dd41047df01d23ee86226556f9a255e90325e6e55fc032a'},
                                         'kubernetes': {'container_name': 'understood-gnat-mysql',
                                                        'namespace_name': 'default',
                                                        'pod_name': 'understood-gnat-mysql-868b556f8f-lwdr9',
                                                        'pod_id': '7913bac3-4221-11e8-8f48-3e9b14d7275e',
                                                        'labels': {'app': 'understood-gnat-mysql',
                                                                   'pod-template-hash': '4246112949'},
                                                        'host': 'minikube',
                                                        'master_url': 'https://10.96.0.1:443/api',
                                                        'namespace_id': '865fc7d1-02a4-11e8-9904-3e9b14d7275e'},
                                         '@timestamp': '2018-04-17T09:28:49+00:00',
                                         '@log_name': 'kubernetes.var.log.containers.understood-gnat'
                                                      '-mysql-868b556f8f-lwdr9_default_understood-gnat'
                                                      '-mysql-5fdafaf3bac39f1c4dd41047df01d23ee86226556f9a255e90325e6e55fc032a.log'}
                                       , 'sort': [1523957329000]},
                    ]

TEST_LOG_ENTRIES = [LogEntry(date='2018-04-17T09:28:39+00:00',
                             content='Warning: Unable to load /usr/share/zoneinfo/right/Factory as time zone. Skipping it.\n',
                             pod_name='understood-gnat-mysql-868b556f8f-lwdr9',
                             namespace='default'),
                    LogEntry(date='2018-04-17T09:28:49+00:00',
                          content='MySQL init process done. Ready for start up.\n',
                          pod_name='understood-gnat-mysql-868b556f8f-lwdr9',
                          namespace='default')]

TEST_SEARCH_OUTPUT_EMPTY = { "took": 6,
                             "timed_out": False,
                             "_shards": {
                               "total": 5,
                               "successful": 5,
                               "skipped": 0,
                               "failed": 0
                             },
                             "hits": {
                               "total": 0,
                               "max_score": None,
                               "hits": []
                             }
                           }


def test_full_log_search(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_scan_mock = mocker.patch('logs_aggregator.k8s_es_client.elasticsearch.helpers.scan')
    es_scan_mock.return_value = iter(TEST_SCAN_OUTPUT)

    assert list(client.get_log_generator()) == TEST_LOG_ENTRIES


def test_full_log_search_filter(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_scan_mock = mocker.patch('logs_aggregator.k8s_es_client.elasticsearch.helpers.scan')
    es_scan_mock.return_value = iter(TEST_SCAN_OUTPUT)

    filter_all_results = list(client.get_log_generator(filters=[lambda x: False]))
    assert filter_all_results == []


def test_full_log_search_filter_idempotent(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_scan_mock = mocker.patch('logs_aggregator.k8s_es_client.elasticsearch.helpers.scan')
    es_scan_mock.return_value = iter(TEST_SCAN_OUTPUT)

    filter_all_results = list(client.get_log_generator(filters=[lambda x: True]))
    assert filter_all_results == TEST_LOG_ENTRIES


def test_get_experiment_logs(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_log_search = mocker.patch.object(client, 'get_log_generator')
    mocked_log_search.return_value = iter(TEST_LOG_ENTRIES)

    experiment_name = 'fake-experiment'
    namespace = 'fake-namespace'

    run_mock = MagicMock(spec=Run)
    run_mock.name = experiment_name

    run_start_date = '2018-04-17T09:28:39+00:00'

    experiment_logs = client.get_experiment_logs_generator(run=run_mock, namespace=namespace,
                                                           start_date=run_start_date)

    for log, expected_log in zip(experiment_logs, TEST_LOG_ENTRIES):
        assert log == expected_log

    mocked_log_search.assert_called_with(query_body={
        "query": {"bool": {"must":
                               [{'term': {'kubernetes.labels.runName.keyword': experiment_name}},
                                {'term': {'kubernetes.namespace_name.keyword': namespace}}
                                ],
                           "filter": {"range": {"@timestamp": {"gte": run_start_date}}}
                           }},
        "sort": {"@timestamp": {"order": "asc"}}},
        filters=[], index='_all')


def test_get_workflow_logs(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_log_search = mocker.patch.object(client, 'get_log_generator')
    mocked_log_search.return_value = iter(TEST_LOG_ENTRIES)

    namespace = 'fake-namespace'

    workflow_name = 'test-workflow'
    workflow_mock = MagicMock(spec=ArgoWorkflow)
    workflow_mock.name = workflow_name

    workflow_start_date = '2018-04-17T09:28:39+00:00'

    experiment_logs = client.get_argo_workflow_logs_generator(workflow=workflow_mock, namespace=namespace,
                                                              start_date=workflow_start_date)

    for log, expected_log in zip(experiment_logs, TEST_LOG_ENTRIES):
        assert log == expected_log

    mocked_log_search.assert_called_with(query_body={
            "query": {"bool": {"must":
                                   [{'term':
                                         {'kubernetes.labels.workflows_argoproj_io/workflow.keyword':
                                              workflow_mock.name}},
                                    {'term': {'kubernetes.namespace_name.keyword': namespace}}
                                    ],
                               "filter": {"range": {"@timestamp": {"gte": workflow_start_date}}}
                               }},
            "sort": {"@timestamp": {"order": "asc"}}},
        filters=[], index='_all')


def test_get_experiment_logs_time_range(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_log_search = mocker.patch.object(client, 'get_log_generator')
    mocked_log_search.return_value = iter(TEST_LOG_ENTRIES)

    experiment_name = 'fake-experiment'
    namespace = 'fake-namespace'

    run_mock = MagicMock(spec=Run)
    run_mock.name = experiment_name

    start_date = '2018-04-17T09:28:39+00:00'
    end_date = '2018-04-17T09:28:49+00:00'

    experiment_logs = client.get_experiment_logs_generator(run=run_mock,
                                                           namespace=namespace,
                                                           start_date=start_date,
                                                           end_date=end_date)

    for log, expected_log in zip(experiment_logs, TEST_LOG_ENTRIES):
        assert log == expected_log

    mocked_log_search.assert_called_with(query_body={
        "query": {"bool": {"must":
                               [{'term': {'kubernetes.labels.runName.keyword': experiment_name}},
                                {'term': {'kubernetes.namespace_name.keyword': namespace}}
                                ],
                           "filter": {"range": {"@timestamp":{"gte": start_date, "lte": end_date}}}
                           }},
        "sort": {"@timestamp": {"order": "asc"}}},
        filters=[], index='_all')


def test_delete_logs_for_namespace(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_delete_logs = mocker.patch.object(client, 'delete_by_query')

    client.delete_logs_for_namespace("namespace")

    assert mocked_delete_logs.call_count == 1


def test_delete_logs_for_run(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_delete_logs = mocker.patch.object(client, 'delete_by_query')

    run_name = 'test_run'
    namespace = 'fake-namespace'

    client.delete_logs_for_run(run_name, namespace)

    delete_query = {"query": {"bool": {"must":
        [
            {"term": {'kubernetes.labels.runName.keyword': run_name}},
            {"term": {'kubernetes.namespace_name.keyword': namespace}}
        ]
    }
    }
    }

    mocked_delete_logs.assert_called_with(index='_all',
                                          body=delete_query)
