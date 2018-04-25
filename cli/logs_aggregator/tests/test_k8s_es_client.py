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

from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from logs_aggregator.k8s_log_entry import LogEntry

TEST_SEARCH_OUTPUT = {'took': 38,
                      'timed_out': False,
                      '_shards': {'total': 10, 'successful': 10, 'skipped': 0, 'failed': 0},
                      'hits': {'total': 2, 'max_score': None,
                               'hits': [
                                   {'_index': 'fluentd-20180417',
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
                                       , 'sort': [1523957329000]}],
                               }
                      }

TEST_POD_LOGS = [LogEntry(date='2018-04-17T09:28:39+00:00',
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


def test_get_pod_logs(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocker.patch.object(client, 'search').return_value = TEST_SEARCH_OUTPUT

    pod_logs = client.get_pod_logs(pod_name='understood-gnat-mysql-868b556f8f-lwdr9')

    assert pod_logs == TEST_POD_LOGS



def test_get_pod_logs_invalid_pod(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocker.patch.object(client, 'search').return_value = TEST_SEARCH_OUTPUT_EMPTY

    pod_logs = client.get_pod_logs(pod_name='not-existing')

    assert pod_logs == []


def test_get_pod_logs_start_date(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_search_mock = mocker.patch.object(client, 'search')
    es_search_mock.return_value = TEST_SEARCH_OUTPUT

    log_entry_timestamp = TEST_POD_LOGS[0].date

    pod_name = 'understood-gnat-mysql-868b556f8f-lwdr9'
    client.get_pod_logs(pod_name=pod_name,
                        start_date=log_entry_timestamp,
                        index='_all',
                        log_count=100,
                        sort='@timestamp:asc')
    es_search_mock.assert_called_once_with(q=f'kubernetes.pod_name:"{pod_name}" '
                                             f'AND @timestamp:[{log_entry_timestamp} TO *]',
                                           index='_all',
                                           size=100,
                                           sort='@timestamp:asc')

def test_get_pod_logs_end_date(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_search_mock = mocker.patch.object(client, 'search')
    es_search_mock.return_value = TEST_SEARCH_OUTPUT


    log_entry_timestamp = TEST_POD_LOGS[0].date

    pod_name = 'understood-gnat-mysql-868b556f8f-lwdr9'
    client.get_pod_logs(pod_name=pod_name,
                        end_date=log_entry_timestamp,
                        index='_all',
                        log_count=100,
                        sort='@timestamp:asc')
    es_search_mock.assert_called_once_with(q=f'kubernetes.pod_name:"{pod_name}" '
                                             f'AND @timestamp:[*'
                                             f' TO {log_entry_timestamp}]',
                                           index='_all',
                                           size=100,
                                           sort='@timestamp:asc')


def test_get_pod_logs_date_range(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    es_search_mock = mocker.patch.object(client, 'search')
    es_search_mock.return_value = TEST_SEARCH_OUTPUT

    first_log_entry_timestamp = TEST_POD_LOGS[0].date
    second_log_entry_timestamp = TEST_POD_LOGS[1].date

    pod_name = 'understood-gnat-mysql-868b556f8f-lwdr9'
    client.get_pod_logs(pod_name=pod_name,
                        start_date=first_log_entry_timestamp,
                        end_date=second_log_entry_timestamp,
                        index='_all',
                        log_count=100,
                        sort='@timestamp:asc')
    es_search_mock.assert_called_once_with(q=f'kubernetes.pod_name:"{pod_name}" '
                                             f'AND @timestamp:[{first_log_entry_timestamp} '
                                             f'TO {second_log_entry_timestamp}]',
                                           index='_all',
                                           size=100,
                                           sort='@timestamp:asc')


def test_get_experiment_logs(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    mocker.patch.object(client, 'get_pod_logs').return_value = TEST_POD_LOGS

    experiment_logs = client.get_experiment_logs(experiment_name='understood-gnat-mysql-868b556f8f-lwdr9')

    assert experiment_logs == TEST_POD_LOGS


def test_get_experiment_logs_pod_ids(mocker):
    client = K8sElasticSearchClient(host='fake', port=8080, namespace='kube-system')
    get_pod_logs_mock = mocker.patch.object(client, 'get_pod_logs')
    get_pod_logs_mock.return_value = TEST_POD_LOGS
    client.get_experiment_logs(experiment_name='myqsl',
                               pod_ids=['understood-gnat-mysql-868b556f8f-A',
                                        'understood-gnat-mysql-868b556f8f-B'],
                               log_count=100)
    get_pod_logs_mock.assert_any_call(pod_name='understood-gnat-mysql-868b556f8f-A',
                                      log_count=100, end_date=None, start_date=None)
    get_pod_logs_mock.assert_any_call(pod_name='understood-gnat-mysql-868b556f8f-B',
                                      log_count=100, end_date=None, start_date=None)
