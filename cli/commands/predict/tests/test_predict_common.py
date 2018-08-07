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

from unittest.mock import MagicMock

from platform_resources.run_model import Run
from commands.experiment.common import RunDescription
from commands.predict.common import start_inference_instance, get_inference_instance_url


def test_start_inference_instance(mocker):
    submit_experiment_mock = mocker.patch('commands.predict.common.submit_experiment')
    fake_experiment = MagicMock()
    submit_experiment_mock.return_value = [fake_experiment], 'bla'

    inference_instance = start_inference_instance(name='', model_location='', model_name='')

    assert inference_instance == fake_experiment


def test_get_inference_instance_url_run_description(mocker):
    fake_instance = MagicMock(spec=RunDescription)
    fake_instance.name = 'inf'
    fake_host = 'https://localhost:8443'
    fake_namespace = 'fake_namespace'
    fake_model_name = 'fake_model'

    get_kubectl_host_mock = mocker.patch('commands.predict.common.get_kubectl_host')
    get_kubectl_host_mock.return_value = fake_host

    get_namespace_mock = mocker.patch('commands.predict.common.get_kubectl_current_context_namespace')
    get_namespace_mock.return_value = fake_namespace

    instance_url = get_inference_instance_url(inference_instance=fake_instance, model_name=fake_model_name)

    assert instance_url == f'{fake_host}/api/v1/namespaces/{fake_namespace}/' \
                           f'services/{fake_instance.name}/proxy/v1/models/{fake_model_name}'


def test_get_inference_instance_url_run(mocker):
    fake_instance = MagicMock(spec=Run)
    fake_model_name = 'fake_model'
    fake_instance.name = 'inf'
    fake_instance.metadata = {'labels': {'modelName': fake_model_name}}
    fake_host = 'https://localhost:8443'
    fake_namespace = 'fake_namespace'

    get_kubectl_host_mock = mocker.patch('commands.predict.common.get_kubectl_host')
    get_kubectl_host_mock.return_value = fake_host

    get_namespace_mock = mocker.patch('commands.predict.common.get_kubectl_current_context_namespace')
    get_namespace_mock.return_value = fake_namespace

    instance_url = get_inference_instance_url(inference_instance=fake_instance)

    assert instance_url == f'{fake_host}/api/v1/namespaces/{fake_namespace}/' \
                           f'services/{fake_instance.name}/proxy/v1/models/{fake_model_name}'
