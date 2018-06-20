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

from functools import partial

from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.k8s_log_entry import LogEntry
from logs_aggregator.log_filters import SeverityLevel, PodStatus

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

    assert list(client.full_log_search()) == TEST_LOG_ENTRIES


def test_full_log_search_filter(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_scan_mock = mocker.patch('logs_aggregator.k8s_es_client.elasticsearch.helpers.scan')
    es_scan_mock.return_value = iter(TEST_SCAN_OUTPUT)

    filter_all_results = list(client.full_log_search(filters=[lambda x: False]))
    assert filter_all_results == []


def test_full_log_search_filter_idempotent(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_scan_mock = mocker.patch('logs_aggregator.k8s_es_client.elasticsearch.helpers.scan')
    es_scan_mock.return_value = iter(TEST_SCAN_OUTPUT)

    filter_all_results = list(client.full_log_search(filters=[lambda x: True]))
    assert filter_all_results == TEST_LOG_ENTRIES


def test_get_experiment_logs(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_log_search = mocker.patch.object(client, 'full_log_search')
    mocked_log_search.return_value = TEST_LOG_ENTRIES

    experiment_name = 'fake-experiment'
    namespace = 'fake-namespace'

    experiment_logs = client.get_experiment_logs(run_name=experiment_name, namespace=namespace)

    assert experiment_logs == TEST_LOG_ENTRIES
    mocked_log_search.assert_called_with(lucene_query=f'kubernetes.labels.runName:"{experiment_name}" ' \
                                                      f'AND kubernetes.namespace_name:"{namespace}"',
                                         filters=[], index='_all')


def test_get_experiment_logs_time_range(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocked_log_search = mocker.patch.object(client, 'full_log_search')
    mocked_log_search.return_value = TEST_LOG_ENTRIES

    experiment_name = 'fake-experiment'
    namespace = 'fake-namespace'

    start_date = '2018-04-17T09:28:39+00:00'
    end_date = '2018-04-17T09:28:49+00:00'

    experiment_logs = client.get_experiment_logs(run_name=experiment_name,
                                                 namespace=namespace,
                                                 start_date=start_date,
                                                 end_date=end_date)

    assert experiment_logs == TEST_LOG_ENTRIES
    mocked_log_search.assert_called_with(lucene_query=f'kubernetes.labels.runName:"{experiment_name}" ' \
                                                      f'AND kubernetes.namespace_name:"{namespace}" ' \
                                                      f'AND @timestamp:[{start_date} TO {end_date}]',
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

    client.delete_logs_for_run(run_name)

    mocked_delete_logs.assert_called_with(index='_all',
                                          body={"query": {"match": {'kubernetes.labels.runName': run_name}}})
