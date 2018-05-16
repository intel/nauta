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

from click.testing import CliRunner

from commands import list_experiments
from platform_resources.experiments import ExperimentShort


TEST_EXPERIMENTS = [ExperimentShort(name='test-experiment', parameters_spec={'a': 1, 'b': 2},
                                    creation_timestamp='2018-04-26T13:43:01Z', submitter='namespace-1',
                                    status='CREATING'),
                    ExperimentShort(name='test-experiment-2', parameters_spec={'a': 1, 'b': 2},
                                    creation_timestamp='2018-05-08T13:05:04Z', submitter='namespace-2',
                                    status='SUBMITTED')]


def test_list_experiments_success(mocker):
    api_list_experiments_mock = mocker.patch("commands.list_experiments.experiments_api.list_experiments")
    api_list_experiments_mock.return_value = TEST_EXPERIMENTS

    get_namespace_mock = mocker.patch("commands.list_experiments.get_kubectl_current_context_namespace")

    runner = CliRunner()
    runner.invoke(list_experiments.list_experiments, [])

    assert get_namespace_mock.call_count == 1
    assert api_list_experiments_mock.call_count == 1, "Experiments were not retrieved"


def test_list_experiments_all_users_success(mocker):
    api_list_experiments_mock = mocker.patch("commands.list_experiments.experiments_api.list_experiments")
    api_list_experiments_mock.return_value = TEST_EXPERIMENTS

    get_namespace_mock = mocker.patch("commands.list_experiments.get_kubectl_current_context_namespace")

    runner = CliRunner()
    runner.invoke(list_experiments.list_experiments, ['--all-users'])

    assert get_namespace_mock.call_count == 0
    assert api_list_experiments_mock.call_count == 1, "Experiments were not retrieved"


def test_list_experiments_failure(mocker):
    api_list_experiments_mock = mocker.patch("commands.list_experiments.experiments_api.list_experiments")
    api_list_experiments_mock.side_effect = RuntimeError

    get_namespace_mock = mocker.patch("commands.list_experiments.get_kubectl_current_context_namespace")
    mocker.patch("sys.exit")

    runner = CliRunner()

    runner.invoke(list_experiments.list_experiments, [])

    assert get_namespace_mock.call_count == 1
    assert api_list_experiments_mock.call_count == 1, "Experiments retrieval was not called"
