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

import time
from collections import namedtuple

from kubernetes.client import CustomObjectsApi
from typing import Optional

from platform_resources.platform_resource import PlatformResource
from util.logger import initialize_logger
from util.config import NAUTA_NAMESPACE, NAUTAConfigMap

logger = initialize_logger(__name__)


class ArgoWorkflow(PlatformResource):
    api_group_name = 'argoproj.io'
    crd_plural_name = 'workflows'
    crd_version = 'v1alpha1'

    ArgoWorkflowCliModel = namedtuple('ArgoWorkflowModel', ['name', 'started_at', 'finished_at', 'submitter', 'phase'])

    def __init__(self, name: str = None, namespace: str = None,
                 started_at: str = None, finished_at: str = None,
                 status: dict = None, phase: str = None, body: dict = None,
                 k8s_custom_object_api: CustomObjectsApi = None):
        super().__init__(k8s_custom_object_api=k8s_custom_object_api, name=name, namespace=namespace, body=body)
        self.started_at = started_at
        self.finished_at = finished_at
        self.status = status
        self.phase = phase

    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict) -> 'ArgoWorkflow':
        return cls(name=object_dict['metadata'].get('name'),
                   namespace=object_dict['metadata'].get('namespace'),
                   started_at=object_dict.get('status', {}).get('startedAt'),
                   finished_at=object_dict.get('status', {}).get('finishedAt'),
                   status=object_dict.get('status', {}),
                   phase=object_dict.get('status', {}).get('phase'),
                   body=object_dict)

    @property
    def cli_representation(self):
        return ArgoWorkflow.ArgoWorkflowCliModel(name=self.name,
                                                 started_at=self.started_at,
                                                 finished_at=self.finished_at,
                                                 submitter=self.namespace,
                                                 phase=self.phase)

    @property
    def parameters(self):
        return {param['name']: param.get('value') for param in self.body['spec']['arguments']['parameters']}

    @parameters.setter
    def parameters(self, parameters_to_set: dict):
        """
        Setting parameters works like passing -p parameters to argo submit command - default values defined in
        workflow spec will remain unchanged, if they are not present in parameters_to_set dict. An KeyError
         will be raised if there is a parameter without value after parameters update.
        :param parameters_to_set: Dictionary with parameter names as keys and parameter values
        """
        for param in self.body['spec']['arguments']['parameters']:
            if parameters_to_set.get(param['name']):
                param['value'] = str(parameters_to_set.get(param['name']))
            elif not param.get('value'):
                raise KeyError(f'Required parameter: {param["name"]} is not set.'
                               f' Parameters to update: {parameters_to_set}'
                               f' Current parameters: {self.body["spec"]["arguments"]["parameters"]}')

    @property
    def generate_name(self) -> Optional[str]:
        return self.body.get('metadata', {}).get('generateName')

    @generate_name.setter
    def generate_name(self, value: str):
        self.body['metadata']['generateName'] = str(value)

    def wait_for_completion(self, timeout=600, poll_interval=3):
        """
        Wait until workflow will enter Succeeded phase. If workflow will enter Failed phase or will not enter
        Succeeded phase in expected time, a RuntimeError will be raised.
        :param timeout: Number of seconds to wait for workflow completion
        :param poll_interval: Interval between workflow status polling in seconds
        :return: None if workflow completes, exception is raised otherwise
        """
        success_phases = {'Succeeded'}
        failure_phases = {'Failed', 'Error'}
        for attempt in range(timeout//poll_interval):
            current_workflow = self.get(name=self.name, namespace=self.namespace)
            current_phase = current_workflow.phase
            if current_phase in success_phases:
                return
            elif current_phase in failure_phases:
                raise RuntimeError(f'Workflow {self.name} entered failure status {current_phase}.'
                                   f'Reason: {current_workflow.status["message"]}')
            else:
                logger.info(f'Waiting for workflow {self.name} to complete. Attempt #{attempt}')
                time.sleep(poll_interval)
        raise RuntimeError(f'Workflow {self.name} has not entered one of statuses {success_phases}'
                           f' in {timeout} seconds.')


class ExperimentImageBuildWorkflow(ArgoWorkflow):
    GIT_REPO_MANAGER_SERVICE = f'nauta-gitea-ssh.{NAUTA_NAMESPACE}'
    DOCKER_REGISTRY_SERVICE = f'nauta-docker-registry.{NAUTA_NAMESPACE}:5000'
    BUILDKITD_SERVICE = f'nauta-buildkit.{NAUTA_NAMESPACE}:1234'

    def __init__(self, username: str = None, experiment_name: str = None,
                 name: str = None, namespace: str = None,
                 started_at: str = None, finished_at: str = None,
                 status: dict = None, phase: str = None, body: dict = None,
                 k8s_custom_object_api: CustomObjectsApi = None, failure_message: str = None):
        super().__init__(k8s_custom_object_api=k8s_custom_object_api, name=name, namespace=namespace, body=body)
        self.started_at = started_at
        self.finished_at = finished_at
        self.status = status
        self.phase = phase
        self.failure_message = failure_message
        self.parameters = {
            'git-address': self.GIT_REPO_MANAGER_SERVICE,
            'docker-registry-address': self.DOCKER_REGISTRY_SERVICE,
            'buildkitd-address': self.BUILDKITD_SERVICE,
            'cluster-registry-address': NAUTAConfigMap().registry,
            'user-name': username,
            'experiment-name': experiment_name
        }
        self.generate_name = f'{experiment_name}-image-build-'
        self.experiment_name = experiment_name


    @property
    def experiment_name(self) -> Optional[str]:
        return self.labels.get('experimentName')

    @experiment_name.setter
    def experiment_name(self, value: str):
        labels = self.labels
        labels['experimentName'] = value
        self.labels = labels
