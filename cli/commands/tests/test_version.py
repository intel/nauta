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

import re

import pytest
from kubernetes.client.models import V1ConfigMap
from click.testing import CliRunner

from commands import version
from version import VERSION
from util.config import DLS4EConfigMap
from util.exceptions import KubectlIntError
from cli_text_consts import VERSION_CMD_TEXTS as TEXTS, VERBOSE_RERUN_MSG


PLATFORM_VERSION = "1.2"

APPLICATION_VERSION_REGEX = r"{application_row_name}[ ]+\| {version}".format(
    application_row_name=TEXTS["table_app_row_name"], version=VERSION
)
PLATFORM_VERSION_ON_SUCCESS_REGEX = r"{platform_row_name}[ ]+\| {version}".format(
    platform_row_name=TEXTS["table_platform_row_name"], version=PLATFORM_VERSION
)
PLATFORM_VERSION_ON_FAIL_REGEX = r"{platform_row_name}[ ]+\| {version}".format(
    platform_row_name=TEXTS["table_platform_row_name"], version=TEXTS["initial_platform_version"]
)


def assert_version_table_rows(cmd_output: str, on_cmd_fail):
    """ Assert that expected application and platform rows are present only once in the command output. """
    application_row_matches = re.findall(APPLICATION_VERSION_REGEX, cmd_output)
    platform_row_matches = re.findall(
        PLATFORM_VERSION_ON_FAIL_REGEX if on_cmd_fail else PLATFORM_VERSION_ON_SUCCESS_REGEX, cmd_output
    )

    assert len(application_row_matches) == 1
    assert len(platform_row_matches) == 1


@pytest.fixture()
def mocked_k8s_CoreV1Api(mocker):
    mocked_coreV1Api_class = mocker.patch('kubernetes.client.CoreV1Api')
    mocker.patch('kubernetes.client.ApiClient')
    coreV1API_instance = mocked_coreV1Api_class.return_value

    v1_config_map = V1ConfigMap(data={DLS4EConfigMap.PLATFORM_VERSION: PLATFORM_VERSION,
                                      DLS4EConfigMap.IMAGE_TILLER_FIELD: "",
                                      DLS4EConfigMap.EXTERNAL_IP_FIELD: "",
                                      DLS4EConfigMap.IMAGE_TENSORBOARD_SERVICE_FIELD: "",
                                      DLS4EConfigMap.REGISTRY_FIELD: ""})

    coreV1API_instance.read_namespaced_config_map.return_value = v1_config_map

    return coreV1API_instance


@pytest.fixture()
def mocked_k8s_config(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    mocked_conf_class = mocker.patch('kubernetes.client.configuration.Configuration')
    conf_instance = mocked_conf_class.return_value
    conf_instance.host = 'https://127.0.0.1:8080'


def test_version(mocked_k8s_config, mocked_k8s_CoreV1Api):
    runner = CliRunner()
    result = runner.invoke(version.version, [])

    assert_version_table_rows(result.output, on_cmd_fail=False)


def test_version_with_kubectl_exception(mocker):
    config_map_mock = mocker.patch('util.config.DLS4EConfigMap.__init__')
    config_map_mock.side_effect = KubectlIntError("")
    runner = CliRunner()
    result = runner.invoke(version.version, [])

    assert_version_table_rows(result.output, on_cmd_fail=True)

    assert TEXTS["kubectl_int_error_msg"] + " " + VERBOSE_RERUN_MSG in result.output


def test_version_with_unknown_exception(mocker):
    config_map_mock = mocker.patch('util.config.DLS4EConfigMap.__init__')
    config_map_mock.side_effect = Exception("")
    runner = CliRunner()
    result = runner.invoke(version.version, [])

    assert_version_table_rows(result.output, on_cmd_fail=True)

    assert TEXTS["other_error_msg"] + " " + VERBOSE_RERUN_MSG in result.output
