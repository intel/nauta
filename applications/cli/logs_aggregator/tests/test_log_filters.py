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

import pytest


from logs_aggregator.log_filters import filter_log_by_severity,filter_log_by_pod_status,\
    SeverityLevel, filter_log_by_pod_ids
from logs_aggregator.k8s_log_entry import LogEntry
from util.k8s.k8s_info import PodStatus

no_severity_log_entry = LogEntry(date='2018-04-19T14:27:46+00:00', content='bla',
                                 pod_name='elasticsearch-5985cbd9d8-5lf55',
                                 namespace='default')
debug_log_entry = LogEntry(date='2018-04-19T14:27:46+00:00', content='[DEBUG ] bla',
                           pod_name='elasticsearch-5985cbd9d8-5lf55',
                           namespace='default')
info_log_entry = LogEntry(date='2018-04-19T14:27:46+00:00', content='[INFO ] bla',
                          pod_name='elasticsearch-5985cbd9d8-5lf55',
                          namespace='default')
warning_log_entry = LogEntry(date='2018-04-19T14:27:46+00:00', content='[WARNING ] bla',
                             pod_name='elasticsearch-5985cbd9d8-5lf55',
                             namespace='default')
error_log_entry = LogEntry(date='2018-04-19T14:27:46+00:00', content='[ERROR ] bla',
                           pod_name='elasticsearch-5985cbd9d8-5lf55',
                           namespace='default')
critical_log_entry = LogEntry(date='2018-04-19T14:27:46+00:00', content='[CRITICAL ] bla',
                              pod_name='elasticsearch-5985cbd9d8-5lf55',
                              namespace='default')


@pytest.mark.parametrize("log_entry", [debug_log_entry, info_log_entry, warning_log_entry,
                                       error_log_entry, critical_log_entry])
def test_filter_log_by_severity_debug(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.DEBUG) == True


@pytest.mark.parametrize("log_entry", [info_log_entry, warning_log_entry,
                                       error_log_entry, critical_log_entry])
def test_filter_log_by_severity_info(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.INFO) == True


@pytest.mark.parametrize("log_entry", [debug_log_entry])
def test_filter_log_by_severity_info_negative(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.INFO) == False


@pytest.mark.parametrize("log_entry", [warning_log_entry,
                                       error_log_entry, critical_log_entry])
def test_filter_log_by_severity_warning(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.WARNING) == True


@pytest.mark.parametrize("log_entry", [debug_log_entry, info_log_entry])
def test_filter_log_by_severity_warning_negative(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.WARNING) == False


@pytest.mark.parametrize("log_entry", [error_log_entry, critical_log_entry])
def test_filter_log_by_severity_error(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.ERROR) == True


@pytest.mark.parametrize("log_entry", [debug_log_entry, info_log_entry, warning_log_entry])
def test_filter_log_by_severity_error_negative(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.ERROR) == False


@pytest.mark.parametrize("log_entry", [critical_log_entry])
def test_filter_log_by_severity_critical(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.CRITICAL) == True


@pytest.mark.parametrize("log_entry", [debug_log_entry, info_log_entry,
                                       warning_log_entry, error_log_entry])
def test_filter_log_by_severity_critical_negative(log_entry):
    assert filter_log_by_severity(log_entry, SeverityLevel.CRITICAL) == False


@pytest.mark.parametrize("status", list(PodStatus))
def test_filter_log_by_pod_status(status, mocker):

    log_entry = LogEntry(date='2018-04-19T14:27:46+00:00',
                        pod_name='test-pod',
                        namespace='default',
                        content='bla')

    mocked_get_pod_status = mocker.patch('logs_aggregator.log_filters.cached_pod_status')
    mocked_get_pod_status.return_value = status

    assert filter_log_by_pod_status(log_entry, status) == True


def test_filter_log_by_pod_ids():
    pod_id =  'test-pod'

    log_entry = LogEntry(date='2018-04-19T14:27:46+00:00',
                        pod_name='test-pod',
                        namespace='default',
                        content='bla')

    assert filter_log_by_pod_ids(pod_ids={pod_id}, log_entry=log_entry) == True
    assert filter_log_by_pod_ids(pod_ids={'another-pod-id'}, log_entry=log_entry) == False
