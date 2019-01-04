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

from unittest.mock import MagicMock

from platform_resources.run import Run
from commands.predict.common import start_inference_instance, get_inference_instance_url


def test_start_inference_instance(mocker):
    submit_experiment_mock = mocker.patch('commands.predict.common.submit_experiment')
    fake_experiment = MagicMock()
    submit_experiment_mock.return_value = [fake_experiment], {}, 'bla'

    inference_instance = start_inference_instance(name='', model_location='', model_name='', local_model_location='')

    assert inference_instance == fake_experiment


def test_get_inference_instance_url_run_description(mocker):
    fake_instance = MagicMock(spec=Run)
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
                           f'services/{fake_instance.name}:rest-port/proxy/v1/models/{fake_model_name}'


def test_get_inference_instance_url_run(mocker):
    fake_instance = MagicMock(spec=Run)
    fake_model_name = 'fake_model'
    fake_instance.name = 'inf'
    fake_instance.metadata = {'annotations': {'modelName': fake_model_name}}
    fake_host = 'https://localhost:8443'
    fake_namespace = 'fake_namespace'

    get_kubectl_host_mock = mocker.patch('commands.predict.common.get_kubectl_host')
    get_kubectl_host_mock.return_value = fake_host

    get_namespace_mock = mocker.patch('commands.predict.common.get_kubectl_current_context_namespace')
    get_namespace_mock.return_value = fake_namespace

    instance_url = get_inference_instance_url(inference_instance=fake_instance)

    assert instance_url == f'{fake_host}/api/v1/namespaces/{fake_namespace}/' \
                           f'services/{fake_instance.name}:rest-port/proxy/v1/models/{fake_model_name}'
