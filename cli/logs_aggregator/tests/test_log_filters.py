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
