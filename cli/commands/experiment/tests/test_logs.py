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

from commands.experiment import logs
from logs_aggregator.k8s_log_entry import LogEntry


TEST_LOG_ENTRIES = [LogEntry(date='2018-04-17T09:28:39+00:00',
                             content='Warning: Unable to load '
                                     '/usr/share/zoneinfo/right/Factory as time zone. Skipping it.\n',
                             pod_name='understood-gnat-mysql-868b556f8f-lwdr9',
                             namespace='default'),
                    LogEntry(date='2018-04-17T09:28:49+00:00',
                             content='MySQL init process done. Ready for start up.\n',
                             pod_name='understood-gnat-mysql-868b556f8f-lwdr9',
                             namespace='default')]


def test_show_logs_success(mocker):
    es_client_mock = mocker.patch("commands.experiment.logs.K8sElasticSearchClient")
    es_client_instance = es_client_mock.return_value
    es_client_instance.get_experiment_logs.return_value = TEST_LOG_ENTRIES

    proxy_mock = mocker.patch.object(logs, 'K8sProxy')

    get_current_namespace_mock = mocker.patch("commands.experiment.logs.get_kubectl_current_context_namespace")
    get_run_mock = mocker.patch("commands.experiment.logs.get_run")

    runner = CliRunner()
    result = runner.invoke(logs.logs, ['fake-experiment'])

    print(result)

    assert proxy_mock.call_count == 1, "port forwarding was not initiated"
    assert get_current_namespace_mock.call_count == 1, "namespace was not retrieved"
    assert get_run_mock.call_count == 1, "run was not retrieved"
    assert es_client_instance.get_experiment_logs.call_count == 1, "Experiment logs were not retrieved"


def test_show_logs_failure(mocker):
    es_client_mock = mocker.patch("commands.experiment.logs.K8sElasticSearchClient")
    es_client_instance = es_client_mock.return_value
    es_client_instance.get_experiment_logs.side_effect = RuntimeError

    proxy_mock = mocker.patch.object(logs, 'K8sProxy')

    get_current_namespace_mock = mocker.patch("commands.experiment.logs.get_kubectl_current_context_namespace")
    get_run_mock = mocker.patch("commands.experiment.logs.get_run")

    runner = CliRunner()

    result = runner.invoke(logs.logs, ['fake-experiment'])

    assert proxy_mock.call_count == 1, "port forwarding was not initiated"
    assert get_current_namespace_mock.call_count == 1, "namespace was not retrieved"
    assert get_run_mock.call_count == 1, "run was not retrieved"
    assert es_client_instance.get_experiment_logs.call_count == 1, "Experiment logs retrieval was not called"
    assert result.exit_code == 1
