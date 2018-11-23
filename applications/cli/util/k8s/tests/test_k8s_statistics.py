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
