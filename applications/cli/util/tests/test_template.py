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

from unittest.mock import patch

import pytest

from util import template
import util.config

RESOURCES_TO_BE_CHANGED = {
    'requests': {'cpu': '10', 'memory': '1G'},
    'limits': {'cpu': '10', 'memory': '10G'}
}

SINGLE_VALUES_SET = {"worker_cpu": "10", "worker_memory": "10G", "memory": "null"}


@pytest.mark.parametrize("input,expected", [("1", 1000), ("1m", 1)])
def test_convert_k8s_cpu_resource(input, expected):
    assert template.convert_k8s_cpu_resource(input) == expected


@pytest.mark.parametrize("input,expected", [("1", 1), ("1Gi", 2 ** 30), ("1G", 10 ** 9), ("1E", 10 ** 18),
                                            ("2Ei", 2 * (2 ** 60)), ("1P", 10 ** 15),
                                            ("3Pi", 3 * (2 ** 50)), ("2T", 2 * 10 ** 12),
                                            ("1Ti", 2 ** 40), ("2M", 2 * 10 ** 6),
                                            ("1Mi", 2 ** 20), ("5K", 5 * 10 ** 3),
                                            ("7Ki", 7 * 2 ** 10)])
def test_convert_k8s_memory_resource(input, expected):
    assert template.convert_k8s_memory_resource(input) == expected


def test_replace_cpu_configuration_without_fraction():

    changed_resources = template.replace_cpu_configuration(RESOURCES_TO_BE_CHANGED, new_cpu_number="1",
                                                           current_cpu_number="20", fraction=None)

    assert changed_resources.get("requests").get("cpu") == "0.5"
    assert changed_resources.get("limits").get("cpu") == "0.5"


def test_replace_cpu_configuration_with_fraction():

    changed_resources = template.replace_cpu_configuration(RESOURCES_TO_BE_CHANGED, new_cpu_number="2",
                                                           current_cpu_number="20", fraction=0.5, system_required="1")

    assert changed_resources.get("requests").get("cpu") == "0.5"
    assert changed_resources.get("limits").get("cpu") == "0.5"


def test_replace_memory_configuration_without_fraction():

    changed_resources = template.replace_memory_configuration(RESOURCES_TO_BE_CHANGED, new_memory_amount="2G",
                                                              current_mem_amount="20G", fraction=None)

    assert changed_resources.get("requests").get("memory") == "100000000"
    assert changed_resources.get("limits").get("memory") == "1000000000"


def test_replace_memory_configuration_with_fraction():

    changed_resources = template.replace_memory_configuration(RESOURCES_TO_BE_CHANGED, new_memory_amount="4G",
                                                              current_mem_amount="20G", fraction=0.5,
                                                              system_required="2G")

    assert changed_resources.get("requests").get("memory") == "1000000000"
    assert changed_resources.get("limits").get("memory") == "1000000000"


def test_replace_single_value_cpu():

    template.replace_single_value(SINGLE_VALUES_SET, new_value="5", current_value="20", key="worker_cpu")

    assert SINGLE_VALUES_SET.get("worker_cpu") == "2.5"


def test_replace_single_value_memory():

    template.replace_single_value(SINGLE_VALUES_SET, new_value="10G", current_value="25G",
                                  key="worker_memory", cpu=False)

    assert SINGLE_VALUES_SET.get("worker_memory") == "4000000000"


def test_replace_single_value_empty():

    template.replace_single_value(SINGLE_VALUES_SET, new_value="10G", current_value="25G",
                                  key="memory", cpu=False)

    assert SINGLE_VALUES_SET.get("memory") == "null"


def test_validate_memory_settings_positive():
    assert template.validate_memory_settings("10G")


def test_validate_memory_settings_negative():
    assert not template.validate_memory_settings("10Ga")


def test_validate_cpu_settings_positive():
    assert template.validate_cpu_settings("10")


def test_validate_cpu_settings_negative():
    assert not template.validate_cpu_settings("10Ga")


def test_get_values_file_location_with_pack(mocker):
    with mocker.patch.object(util.config.Config, "get_config_path", return_value="/config"):  # noqa
        file_location = template.get_values_file_location("test_pack")

    assert file_location == "/config/packs/test_pack/charts/values.yaml"


def test_get_values_file_location_without_pack():
    with patch.object(util.config.Config, "get_config_path", return_value="/config"):  # noqa
        file_location = template.get_values_file_location(None)

    assert file_location == "/config/packs/*/charts/values.yaml"
