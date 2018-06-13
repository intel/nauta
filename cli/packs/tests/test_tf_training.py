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

import unittest.mock as mock
import pytest

import packs.tf_training as tf_training
from util.exceptions import KubectlIntError


SCRIPT_PARAMETERS = "--param1=value1 -param2=value2 param3=value3"
SCRIPT_LOCATION = "training_script.py"
EXPERIMENT_FOLDER = "\HOME\FOLDER"

TEST_YAML_FILE = '''replicaCount: 2
image:
  pullPolicy: IfNotPresent
commandline:
  args:
  - param4=value4
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi
ingress:
  enabled: false
'''

TEST_DOCKERFILE = "t"

t = '''FROM tensorflow/tensorflow

WORKDIR /app

ADD training.py

ENV PYTHONUNBUFFERED 1
'''

EXAMPLE_PACK_TYPE = "example-pack-type"


def test_modify_values_yaml(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock.mock_open, read_data=TEST_YAML_FILE)
    sh_move_mock = mocker.patch("shutil.move")
    yaml_dump_mock = mocker.patch("yaml.dump")

    tf_training.modify_values_yaml(EXPERIMENT_FOLDER, SCRIPT_LOCATION, SCRIPT_PARAMETERS,
                                   experiment_name='test-experiment', pack_type=EXAMPLE_PACK_TYPE, registry_port="1111")

    assert sh_move_mock.call_count == 1, "job yaml file wasn't moved."
    output = yaml_dump_mock.call_args[0][0]
    compare_yaml(output["commandline"]["args"], SCRIPT_LOCATION)

    assert yaml_dump_mock.call_count == 1, "job yaml wasn't modified"
    assert open_mock.call_count == 2, "files weren't read/written"
    assert all(EXAMPLE_PACK_TYPE in call[0][0] for call in open_mock.call_args_list)


def compare_yaml(args_list, script_location):
    assert script_location == args_list[0], "missing script name in list of arguments"
    local_list = str.split(" ")

    index = 1

    for param in local_list:
        assert param == args_list[index], "missing argument"

        index = index + 1


def test_modify_dockerfile(mocker):
    open_mock = mocker.patch("builtins.open", new_callable=mock.mock_open, read_data=TEST_DOCKERFILE)
    sh_move_mock = mocker.patch("shutil.move")

    tf_training.modify_dockerfile(EXPERIMENT_FOLDER, "12345")

    assert sh_move_mock.call_count == 1, "dockerfile wasn't moved"
    assert open_mock.call_count == 2, "dockerfiles weren't read/modified"


def test_update_configuration_success(mocker):
    modify_values_yaml_mock = mocker.patch("packs.tf_training.modify_values_yaml")
    modify_dockerfile_mock = mocker.patch("packs.tf_training.modify_dockerfile")
    modify_draft_toml_mock = mocker.patch("packs.tf_training.modify_draft_toml")

    output = tf_training.update_configuration(EXPERIMENT_FOLDER, SCRIPT_LOCATION,"", SCRIPT_PARAMETERS,
                                              experiment_name='test-experiment', internal_registry_port="12345",
                                              pack_type=EXAMPLE_PACK_TYPE)

    assert not output, "configuration wasn't updated"
    assert modify_dockerfile_mock.call_count == 1, "dockerfile wasn't modified"
    assert modify_values_yaml_mock.call_count == 1, "values yaml wasn't modified"
    assert modify_draft_toml_mock.call_count == 1, "draft toml wasn't modified"


def test_update_configuration_failure(mocker):
    modify_values_yaml_mock = mocker.patch("packs.tf_training.modify_values_yaml")
    modify_dockerfile_mock = mocker.patch("packs.tf_training.modify_dockerfile")

    modify_values_yaml_mock.side_effect = Exception("Test error")
    with pytest.raises(KubectlIntError):
        tf_training.update_configuration(EXPERIMENT_FOLDER, SCRIPT_LOCATION,"", SCRIPT_PARAMETERS,
                                         experiment_name='test-experiment', internal_registry_port="12345",
                                         pack_type=EXAMPLE_PACK_TYPE)

    assert modify_dockerfile_mock.call_count == 0, "dockerfile was modified"
    assert modify_values_yaml_mock.call_count == 1, "values yaml wasn't modified"
