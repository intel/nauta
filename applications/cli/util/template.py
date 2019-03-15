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

import glob
import logging
import re

from ruamel.yaml import YAML
from typing import Dict

from util.config import Config

PREFIX_VALUES = {"E": 10 ** 18, "P": 10 ** 15, "T": 10 ** 12, "G": 10 ** 9, "M": 10 ** 6, "K": 10 ** 3}
PREFIX_I_VALUES = {"Ei": 2 ** 60, "Pi": 2 ** 50, "Ti": 2 ** 40, "Gi": 2 ** 30, "Mi": 2 ** 20, "Ki": 2 ** 10}

RESOURCE_NAMES = ["worker_resources", "ps_resources", "resources"]
CPU_SINGLE_VALUES = ["worker_cpu", "ps_cpu", "cpu", "cpus"]
MEMORY_SINGLE_VALUES = ["worker_memory", "ps_memory", "memory"]

CPU_FRACTION = "cpu_fraction"
MEMORY_FRACTION = "memory_fraction"

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def convert_k8s_cpu_resource(cpu_resource: str) -> float:
    # If CPU resources are gives as for example 100m, we simply strip last character and sum leftover numbers.
    cpu_resource = str(cpu_resource)
    if str(cpu_resource[-1]) == "m":
        return int(str(cpu_resource[:-1]))
    # Else we assume that cpu resources are given as float value of normal CPUs instead of miliCPUs.
    else:
        return int(float(cpu_resource) * 1000)


def convert_k8s_memory_resource(mem_resource: str) -> int:
    # If last character is "i" then assume that resource is given as for example 1000Ki.
    mem_resource = str(mem_resource)
    if mem_resource[-1] == "i" and mem_resource[-2:] in PREFIX_I_VALUES:
        prefix = mem_resource[-2:]
        return int(float(mem_resource[:-2]) * PREFIX_I_VALUES[prefix])
    # If last character is one of the normal exponent prefixes (with base 10) then assume that resource is given
    # as for example 1000K.
    elif mem_resource[-1] in PREFIX_VALUES:
        prefix = mem_resource[-1]
        return int(float(mem_resource[:-1]) * PREFIX_VALUES[prefix])
    # If there is e contained inside resource string then assume that it is given in exponential format.
    elif "e" in mem_resource:
        return int(float(mem_resource))
    else:
        return int(mem_resource)


def replace_cpu_configuration(data: Dict, new_cpu_number: str, current_cpu_number: str, fraction: float,
                              system_required_min: str = '0', system_required_percent: str ='0') -> Dict:

    if not data:
        return {}

    conv_new_cpu_number = convert_k8s_cpu_resource(new_cpu_number)
    conv_current_cpu_number = convert_k8s_cpu_resource(current_cpu_number)

    if fraction:
        conv_system_required_min = convert_k8s_cpu_resource(system_required_min)
        conv_system_required_percent = float(system_required_percent)/100

        conv_system_required = conv_new_cpu_number * conv_system_required_percent
        if conv_system_required < conv_system_required_min:
            conv_system_required = conv_system_required_min

        new_req_cpu = ((conv_new_cpu_number - conv_system_required) * fraction)/1000
        new_limit_cpu = ((conv_new_cpu_number - conv_system_required) * fraction)/1000
    else:
        req_cpu = convert_k8s_cpu_resource(data.get("requests").get("cpu"))
        limit_cpu = convert_k8s_cpu_resource(data.get("limits").get("cpu"))

        new_req_cpu = (conv_new_cpu_number * req_cpu/conv_current_cpu_number)/1000
        new_limit_cpu = (conv_new_cpu_number * limit_cpu/conv_current_cpu_number)/1000

    data["requests"].update({"cpu": str(new_req_cpu)})
    data["limits"].update({"cpu": str(new_limit_cpu)})
    return data


def replace_memory_configuration(data: Dict, new_memory_amount: str, current_mem_amount: str, fraction: float,
                                 system_required_min: str = '0', system_required_percent: str = '0') -> Dict:

    if not data:
        return {}

    conv_new_memory_amount = convert_k8s_memory_resource(new_memory_amount)
    conv_current_memory_amount = convert_k8s_memory_resource(current_mem_amount)

    if fraction:
        conv_system_required_min = convert_k8s_memory_resource(system_required_min)
        conv_system_required_percent = float(system_required_percent)/100

        conv_system_required = conv_new_memory_amount * conv_system_required_percent
        if conv_system_required < conv_system_required_min:
            conv_system_required = conv_system_required_min

        new_req_memory = int(((conv_new_memory_amount - conv_system_required) * fraction))
        new_limit_memory = int(((conv_new_memory_amount - conv_system_required) * fraction))
    else:
        req_memory = convert_k8s_memory_resource(data.get("requests").get("memory"))
        limit_memory = convert_k8s_memory_resource(data.get("limits").get("memory"))

        new_req_memory = int(conv_new_memory_amount * req_memory/conv_current_memory_amount)
        new_limit_memory = int(conv_new_memory_amount * limit_memory/conv_current_memory_amount)

    data["requests"].update({"memory": str(new_req_memory)})
    data["limits"].update({"memory": str(new_limit_memory)})
    return data


def replace_single_value(data: Dict, new_value: str, current_value: str, key: str, fraction: float = None,
                         cpu: bool = True, system_required_min: str = '0', system_required_percent: str ='0'):
    value = data.get(key)

    if not value or value == "null":
        return

    conv_system_required_percent = float(system_required_percent)/100

    if cpu:
        conv_new_value = convert_k8s_cpu_resource(new_value)
        conv_system_required_min = convert_k8s_cpu_resource(system_required_min)

        conv_system_required = conv_new_value * conv_system_required_percent
        if conv_system_required < conv_system_required_min:
            conv_system_required = conv_system_required_min

        if fraction:
            coefficient = fraction
            conv_new_value = conv_new_value - conv_system_required
        else:
            conv_current_value = convert_k8s_cpu_resource(current_value)
            conv_value = convert_k8s_cpu_resource(value)
            coefficient = conv_value / conv_current_value
        final_value = (conv_new_value * coefficient)/1000
    else:
        conv_new_value = convert_k8s_memory_resource(new_value)
        conv_system_required_min = convert_k8s_memory_resource(system_required_min)

        conv_system_required = conv_new_value * conv_system_required_percent
        if conv_system_required < conv_system_required_min:
            conv_system_required = conv_system_required_min

        if fraction:
            coefficient = fraction
            conv_new_value = conv_new_value - conv_system_required
        else:
            conv_current_value = convert_k8s_memory_resource(current_value)
            conv_value = convert_k8s_memory_resource(value)
            coefficient = conv_value / conv_current_value
        final_value = int(conv_new_value * coefficient)

    data[key] = str(final_value)


def override_values_in_packs(new_cpu_number: str, new_memory_amount: str,
                             current_cpu_number: str, current_mem_amount: str,
                             cpu_system_required_min: str, cpu_system_required_percent: str,
                             mem_system_required_min: str, mem_system_required_percent: str,
                             pack_name: str = None):
    yaml_parser = YAML(typ="jinja2", plug_ins=["ruamel.yaml.jinja2.__plug_in__"])
    values_yaml_paths = get_values_file_location(pack_name)

    for values_yaml_path in glob.glob(values_yaml_paths):
        logger.info(f"Changing resources for pack: {values_yaml_path}")

        with open(values_yaml_path, mode="r") as values_yaml_file:
            pack_values = yaml_parser.load(values_yaml_file)

            if not pack_values:
                logger.error(f"{values_yaml_path} file empty!")
                raise ValueError

            try:
                cpu_fraction = pack_values.get(CPU_FRACTION)
                if cpu_fraction:
                    cpu_fraction = float(cpu_fraction)

                for resource_name in RESOURCE_NAMES:
                    if pack_values.get(resource_name):
                        pack_values[resource_name] = \
                            replace_cpu_configuration(data=pack_values.get(resource_name),
                                                      new_cpu_number=new_cpu_number,
                                                      current_cpu_number=current_cpu_number,
                                                      fraction=cpu_fraction,
                                                      system_required_min=cpu_system_required_min,
                                                      system_required_percent=cpu_system_required_percent)

                for cpu_single_value in CPU_SINGLE_VALUES:
                    replace_single_value(data=pack_values, new_value=new_cpu_number, current_value=current_cpu_number,
                                         key=cpu_single_value, fraction=cpu_fraction,
                                         system_required_min=cpu_system_required_min,
                                         system_required_percent=cpu_system_required_percent)

            except Exception:
                logger.exception("Exception during calculation of new cpu values.")
                raise ValueError

            try:
                memory_fraction = pack_values.get(MEMORY_FRACTION)
                if memory_fraction:
                    memory_fraction = float(memory_fraction)

                for resource_name in RESOURCE_NAMES:
                    if pack_values.get(resource_name):
                        pack_values[resource_name] = \
                            replace_memory_configuration(data=pack_values.get(resource_name),
                                                         new_memory_amount=new_memory_amount,
                                                         current_mem_amount=current_mem_amount,
                                                         fraction=memory_fraction,
                                                         system_required_min=mem_system_required_min,
                                                         system_required_percent=mem_system_required_percent)

                for memory_single_value in MEMORY_SINGLE_VALUES:
                    replace_single_value(data=pack_values, new_value=new_memory_amount,
                                         current_value=current_mem_amount, key=memory_single_value,
                                         fraction=memory_fraction,
                                         system_required_min=mem_system_required_min,
                                         system_required_percent=mem_system_required_percent,
                                         cpu=False)

            except Exception:
                logger.exception("Exception during calculation of new memory values.")
                raise ValueError

        with open(values_yaml_path, mode='w') as values_yaml_file:
            yaml_parser.dump(pack_values, values_yaml_file)
            logger.info(f"Resources for pack: {values_yaml_path} were changed.\n")


def validate_memory_settings(memory: str):
    return re.match(r"^[0-9]+[E|P|T|G|M|K]?[i]?$", memory)


def validate_cpu_settings(cpu: str):
    return re.match(r"^[0-9.]+m?$", cpu)


def get_values_file_location(pack_name: str = None):
    dlsctl_config_dir_path = Config().get_config_path()
    pack = "*" if not pack_name else pack_name
    return f"{dlsctl_config_dir_path}/packs/{pack}/charts/values.yaml"
