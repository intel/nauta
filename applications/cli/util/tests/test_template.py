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

from unittest.mock import patch, mock_open

import pytest

from util import template
import util.config
from util.system import get_current_os, OS

RESOURCES_TO_BE_CHANGED = {
    'requests': {'cpu': '10', 'memory': '1G'},
    'limits': {'cpu': '10', 'memory': '10G'}
}

SINGLE_VALUES_SET = {"worker_cpu": "10", "worker_memory": "10G", "memory": "null"}

VALUES_FILE = {"resources": {"requests": {"cpu": "10", "memory": "10Gi"},
                             "limits": {"cpu": "10", "memory": "10Gi"}},
               "cpu": "10", "memory": "10Gi"}

TEST_PACK_NAME = "test_pack"


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
                                                           current_cpu_number="20", fraction=0.5,
                                                           system_required_min="0.5",
                                                           system_required_percent="0.5")

    assert changed_resources.get("requests").get("cpu") == "0.75"
    assert changed_resources.get("limits").get("cpu") == "0.75"


def test_replace_cpu_configuration_with_fraction_over_min():

    changed_resources = template.replace_cpu_configuration(RESOURCES_TO_BE_CHANGED, new_cpu_number="200",
                                                           current_cpu_number="20", fraction=0.5,
                                                           system_required_min="0.5",
                                                           system_required_percent="0.5")

    assert changed_resources.get("requests").get("cpu") == "99.5"
    assert changed_resources.get("limits").get("cpu") == "99.5"


def test_replace_memory_configuration_without_fraction():

    changed_resources = template.replace_memory_configuration(RESOURCES_TO_BE_CHANGED, new_memory_amount="2G",
                                                              current_mem_amount="20G", fraction=None)

    assert changed_resources.get("requests").get("memory") == "100000000"
    assert changed_resources.get("limits").get("memory") == "1000000000"


def test_replace_memory_configuration_with_fraction():

    changed_resources = template.replace_memory_configuration(RESOURCES_TO_BE_CHANGED, new_memory_amount="4G",
                                                              current_mem_amount="20G", fraction=0.5,
                                                              system_required_min="2G",
                                                              system_required_percent="0.5")

    assert changed_resources.get("requests").get("memory") == "1000000000"
    assert changed_resources.get("limits").get("memory") == "1000000000"


def test_replace_memory_configuration_with_fraction_over_min():

    changed_resources = template.replace_memory_configuration(RESOURCES_TO_BE_CHANGED, new_memory_amount="80G",
                                                              current_mem_amount="20G", fraction=0.5,
                                                              system_required_min="2G",
                                                              system_required_percent="5")

    assert changed_resources.get("requests").get("memory") == "38000000000"
    assert changed_resources.get("limits").get("memory") == "38000000000"


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


def test_extract_pack_name_from_path_success():
    pack_name = "test_pack_name"
    if get_current_os() == OS.WINDOWS:
        path_to_check = f"C:\\dist\\config\\packs\\{pack_name}\\charts\\values.yaml"
    else:
        path_to_check = f"dist/config/packs/{pack_name}/charts/values.yaml"

    ret_pack_name = template.extract_pack_name_from_path(path_to_check)

    assert ret_pack_name == pack_name


def test_extract_pack_name_from_path_lack_of_file():
    pack_name = "test_pack_name"
    if get_current_os() == OS.WINDOWS:
        path_to_check = f"C:\\dist\\config\\packs\\{pack_name}\\charts"
    else:
        path_to_check = f"dist/config/packs/{pack_name}/charts"

    ret_pack_name = template.extract_pack_name_from_path(path_to_check)

    assert not ret_pack_name


def test_extract_pack_name_from_path_folder_too_short():
    pack_name = "test_pack_name"
    if get_current_os() == OS.WINDOWS:
        path_to_check = f"C:\\{pack_name}\\charts"
    else:
        path_to_check = f"/{pack_name}/charts"

    ret_pack_name = template.extract_pack_name_from_path(path_to_check)

    assert not ret_pack_name


class VerifyMocks:
    def __init__(self, mocker):
        self.mocker = mocker
        self.gvfl_mock = mocker.patch("util.template.get_values_file_location")
        self.gwmr_mock = mocker.patch("util.template.get_k8s_worker_min_resources", return_value=("10", " 10Gi"))
        self.glob_mock = mocker.patch("glob.glob", return_value=["test_file"])
        self.epnp_mock = mocker.patch("util.template.extract_pack_name_from_path", return_value=TEST_PACK_NAME)
        self.yaml_mock = mocker.patch("util.template.YAML", )
        self.yaml_mock.return_value.load.return_value = VALUES_FILE


@pytest.fixture
def prepare_mocks(mocker) -> VerifyMocks:
    return VerifyMocks(mocker=mocker)


def test_verfiy_values_in_packs_success(prepare_mocks: VerifyMocks):
    with patch("builtins.open", mock_open(read_data=VALUES_FILE)):
        list_of_packs = template.verify_values_in_packs()

        assert not list_of_packs


def test_verfiy_values_in_packs_cpu_failure(prepare_mocks: VerifyMocks):
    prepare_mocks.gwmr_mock.return_value = ("5", "10Gi")
    with patch("builtins.open", mock_open(read_data=VALUES_FILE)):
        list_of_packs = template.verify_values_in_packs()

        assert len(list_of_packs) == 1
        assert TEST_PACK_NAME in list_of_packs[0]


def test_verfiy_values_in_packs_memory_failure(prepare_mocks: VerifyMocks):
    prepare_mocks.gwmr_mock.return_value = ("10", "5Gi")
    with patch("builtins.open", mock_open(read_data=VALUES_FILE)):
        list_of_packs = template.verify_values_in_packs()

        assert len(list_of_packs) == 1
        assert TEST_PACK_NAME in list_of_packs[0]
