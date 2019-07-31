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

from click.testing import CliRunner
from unittest.mock import patch, mock_open

from cli_text_consts import ConfigCmdTexts as Texts
from commands.config import config, update_resources_in_packs
import util.config

WRONG_CONFIGURATION_FILE = "cpu_number: 10"

CORRECT_CONFIGURATION_FILE = "cpu_number: 10 \n" \
                             "memory_amount: 100Gi"

CORRECT_CONFIGURATION_FILE_W_FRACTIONS = "cpu_number: 10 \n" \
                                         "memory_amount: 100Gi \n" \
                                         "cpu_fraction: 0.5 \n" \
                                         "memory_fraction: 0.5"


def test_nauta_config(mocker):
    nauta_config = mocker.patch("commands.config.NAUTAConfigMap")
    nauta_config.return_value.minimal_node_memory_amount = "2G"
    nauta_config.return_value.minimal_node_cpu_number = "2"


def test_config_missing_arguments():

    runner = CliRunner()

    result = runner.invoke(config)

    assert Texts.MISSING_ARGUMENTS in result.output


def test_config_incorrect_cpu_format(mocker):
    mocker.patch("os.path.join", return_value="config")
    runner = CliRunner()

    with patch.object(util.config.Config, 'get_config_path', return_value="/config"):  # noqa
        result = runner.invoke(config, ["--cpu", "aaa", "--memory", "10G"])

    assert Texts.CPU_WRONG_FORMAT in result.output


def test_config_incorrect_memory_format(mocker):
    mocker.patch("os.path.join", return_value="config")
    runner = CliRunner()

    with patch.object(util.config.Config, 'get_config_path', return_value="/config"):  # noqa
        result = runner.invoke(config, ["--cpu", "10", "--memory", "10Ga"])

    assert Texts.MEMORY_WRONG_FORMAT in result.output


def test_config_cpu_number_too_low(mocker):
    mocker.patch("os.path.join", return_value="config")
    test_nauta_config(mocker)
    runner = CliRunner()

    with patch.object(util.config.Config, 'get_config_path', return_value="/config"):  # noqa
        result = runner.invoke(config, ["--cpu", "1", "--memory", "10G"])

    assert Texts.CPU_SETTINGS_TOO_LOW.format(cpu_value="2") in result.output


def test_config_memory_amount_too_low(mocker):
    mocker.patch("os.path.join", return_value="config")
    test_nauta_config(mocker)
    runner = CliRunner()

    with patch.object(util.config.Config, 'get_config_path', return_value="/config"):  # noqa
        result = runner.invoke(config, ["--cpu", "4", "--memory", "1G"])

    assert Texts.MEMORY_SETTINGS_TOO_LOW.format(memory_value="2G") in result.output


def test_config_non_existing_config_file(mocker):
    mocker.patch("os.path.join", return_value="config")
    mocker.patch("os.path.isfile", return_value=False)
    test_nauta_config(mocker)
    runner = CliRunner()

    with patch.object(util.config.Config, 'get_config_path', return_value="/config"):  # noqa
        result = runner.invoke(config, ["--cpu", "10", "--memory", "10G"])

    assert Texts.MISSING_CONFIG_FILE in result.output


def test_error_during_changing_configuration(mocker):
    mocker.patch("os.path.join", return_value="config")
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("commands.config.spinner")
    ovvp_mock = mocker.patch("commands.config.override_values_in_packs", side_effect=RuntimeError)
    test_nauta_config(mocker)
    runner = CliRunner()

    with patch("builtins.open", mock_open(read_data=CORRECT_CONFIGURATION_FILE)), \
         patch.object(util.config.Config, "get_config_path", return_value=""):  # noqa
        result = runner.invoke(config, ["--cpu", "10", "--memory", "10G"])

    assert Texts.ERROR_DURING_UPDATE in result.output
    assert ovvp_mock.call_count == 1


def test_change_configuration_success(mocker):
    mocker.patch("os.path.join", return_value="config")
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("commands.config.spinner")
    ovvp_mock = mocker.patch("commands.config.override_values_in_packs")
    test_nauta_config(mocker)

    runner = CliRunner()

    with patch("builtins.open", mock_open(read_data=CORRECT_CONFIGURATION_FILE)), \
         patch.object(util.config.Config, "get_config_path", return_value=""):  # noqa
        result = runner.invoke(config, ["--cpu", "10", "--memory", "10G"])

    assert Texts.SUCCESS_MESSAGE in result.output
    assert ovvp_mock.call_count == 1


def test_incorrect_config_file(mocker):
    mocker.patch("os.path.join", return_value="config")
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("commands.config.spinner")
    mocker.patch("commands.config.NAUTAConfigMap")
    sys_exit_mock = mocker.patch("sys.exit")

    with patch("builtins.open", mock_open(read_data=WRONG_CONFIGURATION_FILE)), \
         patch.object(util.config.Config, "get_config_path", return_value=""):  # noqa
        update_resources_in_packs()

    assert sys_exit_mock.call_count == 1, "program didn't exit"
