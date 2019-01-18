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

from operator import itemgetter

from typing import List, Tuple
from util.k8s.kubectl import get_top_for_pod
from util.k8s.k8s_info import get_pods, sum_cpu_resources_unformatted, sum_mem_resources_unformatted, \
    format_mem_resources, format_cpu_resources, PodStatus
from util.logger import initialize_logger

logger = initialize_logger(__name__)


class ResourceUsage():

    def __init__(self, user_name: str, cpu_usage: int, mem_usage: int):
        self.user_name = user_name
        self.cpu_usage = cpu_usage
        self.mem_usage = mem_usage

    def get_formatted_cpu_usage(self):
        return format_cpu_resources(self.cpu_usage)

    def get_formatted_mem_usage(self):
        return format_mem_resources(self.mem_usage)

    def __str__(self):
        return self.user_name+":"+self.get_formatted_cpu_usage()+":"+self.get_formatted_mem_usage()


def get_highest_usage() -> Tuple[List[str], List[str]]:

    available_pods = get_pods(None)
    CPU_KEY = "cpu"
    MEM_KEY = "mem"
    NAME_KEY = "name"

    users_data = {}
    summarized_usage = []

    for item in available_pods:
        name = item.metadata.name
        namespace = item.metadata.namespace
        # omit technical namespaces
        if namespace not in ["nauta", "kube-system"] and item.status.phase.upper() == PodStatus.RUNNING.value:
            try:
                cpu, mem = get_top_for_pod(name=name, namespace=namespace)
                if namespace in users_data:
                    users_data.get(namespace).get(CPU_KEY).append(cpu)
                    users_data.get(namespace).get(MEM_KEY).append(mem)
                else:
                    users_data[namespace] = {CPU_KEY: [cpu], MEM_KEY: [mem]}
            except Exception as exe:
                logger.exception("Error during gathering pod resources usage.")

    for user_name, usage in users_data.items():
        summarized_usage.append({NAME_KEY: user_name,
                                 CPU_KEY: sum_cpu_resources_unformatted(usage.get(CPU_KEY)),
                                 MEM_KEY: sum_mem_resources_unformatted(usage.get(MEM_KEY))})

    top_cpu_users = sorted(summarized_usage, key=itemgetter(CPU_KEY), reverse=True)
    top_mem_users = sorted(summarized_usage, key=itemgetter(MEM_KEY), reverse=True)

    return [ResourceUsage(item[NAME_KEY], item[CPU_KEY], item[MEM_KEY]) for item in top_cpu_users], \
           [ResourceUsage(item[NAME_KEY], item[CPU_KEY], item[MEM_KEY]) for item in top_mem_users]
