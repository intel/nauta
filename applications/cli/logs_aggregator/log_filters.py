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
