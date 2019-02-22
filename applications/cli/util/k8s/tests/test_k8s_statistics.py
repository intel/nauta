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

from kubernetes.client.models import V1ObjectMeta, V1Pod, V1PodStatus
from util.k8s.k8s_info import PodStatus


from util.k8s.k8s_statistics import get_highest_usage

CPU_USER_NAME = "cpu_user_name"
MEM_USER_NAME = "mem_user_name"

PODS = [V1Pod(metadata=V1ObjectMeta(name="cpu_first_pod", namespace=CPU_USER_NAME),
              status=V1PodStatus(phase=PodStatus.RUNNING.value)),
        V1Pod(metadata=V1ObjectMeta(name="mem_first_pod", namespace=MEM_USER_NAME),
              status=V1PodStatus(phase=PodStatus.RUNNING.value)),
        V1Pod(metadata=V1ObjectMeta(name="cpu_second_pod", namespace=CPU_USER_NAME),
              status=V1PodStatus(phase=PodStatus.RUNNING.value)),
        V1Pod(metadata=V1ObjectMeta(name="mem_second_pod", namespace=MEM_USER_NAME),
              status=V1PodStatus(phase=PodStatus.RUNNING.value)),
        V1Pod(metadata=V1ObjectMeta(name="tech_pod", namespace="kube-system"),
              status=V1PodStatus(phase=PodStatus.RUNNING.value))]

TOP_RESULTS = [("3m", "200Ki"), ("2m", "400Ki"), ("3m", "200Ki"), ("2m", "400Ki")]


def test_get_highest_usage_success(mocker):
    get_pods_mock = mocker.patch("util.k8s.k8s_statistics.get_pods")
    get_pods_mock.return_value = PODS
    top_mock = mocker.patch("util.k8s.k8s_statistics.get_top_for_pod")
    top_mock.side_effect = TOP_RESULTS

    top_cpu_users, top_mem_users = get_highest_usage()

    assert len(top_cpu_users) == 2
    assert len(top_mem_users) == 2
    assert top_cpu_users[0].user_name == CPU_USER_NAME
    assert top_mem_users[0].user_name == MEM_USER_NAME
    assert top_cpu_users[0].cpu_usage == 6
    assert top_cpu_users[0].mem_usage == 409600
    assert top_mem_users[0].cpu_usage == 4
    assert top_mem_users[0].mem_usage == 819200
