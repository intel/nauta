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

from logs_aggregator.log_filters import filter_logs_by_severity, SeverityLevel
from logs_aggregator.k8s_log_entry import LogEntry


def test_filter_logs_by_severity():
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
    test_logs = [no_severity_log_entry, debug_log_entry, info_log_entry,
                 warning_log_entry, error_log_entry, critical_log_entry]

    assert (filter_logs_by_severity(logs=test_logs, min_severity=SeverityLevel.DEBUG)
            == [debug_log_entry, info_log_entry, warning_log_entry, error_log_entry, critical_log_entry])
    assert (filter_logs_by_severity(logs=test_logs, min_severity=SeverityLevel.INFO)
            == [info_log_entry, warning_log_entry, error_log_entry, critical_log_entry])
    assert (filter_logs_by_severity(logs=test_logs, min_severity=SeverityLevel.WARNING)
            == [warning_log_entry, error_log_entry, critical_log_entry])
    assert (filter_logs_by_severity(logs=test_logs, min_severity=SeverityLevel.ERROR)
            == [error_log_entry, critical_log_entry])
    assert (filter_logs_by_severity(logs=test_logs, min_severity=SeverityLevel.CRITICAL)
            == [critical_log_entry])


def test_filter_logs_by_pod_status():
    running_pod_log = LogEntry(date='2018-04-19T14:27:46+00:00',
                               pod_name='running-pod',
                               namespace='default',
                               content='bla')

    failed_pod_log = LogEntry(date='2018-04-19T14:27:46+00:00',
                              pod_name='failed-pod',
                              namespace='default',
                              content='bla')



    