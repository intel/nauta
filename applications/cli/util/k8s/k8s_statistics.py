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
        if namespace not in ["dls4e", "kube-system"] and item.status.phase.upper() == PodStatus.RUNNING.value:
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
