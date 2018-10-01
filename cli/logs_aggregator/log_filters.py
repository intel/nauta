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

from enum import Enum
from functools import lru_cache
from typing import Set

from logs_aggregator.k8s_log_entry import LogEntry
from util.logger import initialize_logger
from util.k8s.k8s_info import PodStatus, get_pod_status

log = initialize_logger(__name__)


class SeverityLevel(Enum):
    """
    Helper enum that for given severity level returns set of all severity levels of the same or higher importance.
    """
    CRITICAL = {'CRITICAL'}
    ERROR = {'ERROR', 'CRITICAL'}
    WARNING = {'ERROR', 'CRITICAL', 'WARNING'}
    INFO = {'ERROR', 'CRITICAL', 'WARNING', 'INFO'}
    DEBUG = {'ERROR', 'CRITICAL', 'WARNING', 'INFO', 'DEBUG'}


def filter_log_by_severity(log_entry: LogEntry,
                           min_severity: SeverityLevel) -> bool:
    return any(severity in log_entry.content.upper() for severity in min_severity.value)


@lru_cache(maxsize=128)
def cached_pod_status(pod_name: str, namespace: str) -> PodStatus:
    """
    Wrapper for caching Pod status calls in LRU cache.
    """
    return get_pod_status(pod_name=pod_name, namespace=namespace)


def filter_log_by_pod_status(log_entry: LogEntry, pod_status: PodStatus) -> bool:
    return cached_pod_status(pod_name=log_entry.pod_name, namespace=log_entry.namespace) == pod_status


def filter_log_by_pod_ids(log_entry: LogEntry, pod_ids: Set[str]) -> bool:
    return log_entry.pod_name in pod_ids
