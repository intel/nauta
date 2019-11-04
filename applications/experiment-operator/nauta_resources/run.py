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


from datetime import datetime, timezone
from http import HTTPStatus
from dateutil import parser
from enum import Enum
from typing import List, Optional

from kubernetes_asyncio.client import V1Pod
from kubernetes_asyncio.client.rest import ApiException

from nauta_resources.platform_resource import CustomResource, K8SApiClient


class RunKinds(Enum):
    TRAINING = "training"
    JUPYTER = "jupyter"
    INFERENCE = "inference"


class RunStatus(Enum):
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    COMPLETE = 'COMPLETE'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'
    CREATING = 'CREATING'


class Run(CustomResource):
    api_group_name = 'aipg.intel.com'
    crd_plural_name = 'runs'
    crd_version = 'v1'

    def __init__(self, name: str, body: dict = None, namespace: str = None, *, parameters: List[str] = None,
                 state: RunStatus = None, pod_count: int = None, pod_selector: dict = None, experiment_name: str = None,
                 metrics: dict = None, template_name: str = None,
                 start_timestamp: str = None, end_timestamp: str = None):
        if not body:
            body = {
                'apiVersion': f'{self.api_group_name}/{self.crd_version}',
                'kind': self.__class__.__name__,
                'metadata': {'name': name, 'namespace': namespace}
            }
        super().__init__(name=name, namespace=namespace, body=body)
        if name:
            self.name = name
        if parameters:
            self.parameters = parameters
        if state:
            self.state = state
        if pod_count:
            self.pod_count = pod_count
        if pod_selector:
            self.pod_selector = pod_selector
        if experiment_name:
            self.experiment_name = experiment_name
        if metrics:
            self.metrics = metrics
        if template_name:
            self.template_name = template_name
        if start_timestamp:
            self.start_timestamp = start_timestamp
        if end_timestamp:
            self.end_timestamp = end_timestamp

        # Reset update fields container
        self._fields_to_update = set()

    @property
    def name(self) -> str:
        return self._body.get('metadata', {}).get('name')

    @name.setter
    def name(self, value: str):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['name'] = value
        self._body['metadata']['name'] = value

    @property
    def parameters(self) -> List[str]:
        return self._body.get('spec', {}).get('parameters')

    @parameters.setter
    def parameters(self, value: List[str]):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['parameters'] = value
        self._fields_to_update.add('spec.parameters')

    @property
    def state(self) -> RunStatus:
        state_in_body = self._body.get('spec', {}).get('state')
        return RunStatus[self._body.get('spec', {}).get('state')] if state_in_body else RunStatus.CREATING

    @state.setter
    def state(self, value: RunStatus):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['state'] = str(value.value)
        self._fields_to_update.add('spec.state')

    @property
    def pod_count(self) -> int:
        return self._body.get('spec', {}).get('pod-count')

    @pod_count.setter
    def pod_count(self, value: int):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['pod-count'] = int(value)
        self._fields_to_update.add('spec.pod-count')

    @property
    def pod_selector(self) -> dict:
        return self._body.get('spec', {}).get('pod-selector')

    @pod_selector.setter
    def pod_selector(self, value: dict):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['pod-selector'] = value
        self._fields_to_update.add('spec.pod-selector')

    @property
    def experiment_name(self) -> str:
        return self._body.get('spec', {}).get('experiment-name')

    @experiment_name.setter
    def experiment_name(self, value: str):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['experiment-name'] = str(value)
        self._fields_to_update.add('spec.experiment-name')

    @property
    def metrics(self) -> dict:
        return self._body.get('spec', {}).get('metrics', {})

    @metrics.setter
    def metrics(self, value: dict):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['metrics'] = value
        self._fields_to_update.add('spec.metrics')

    @property
    def template_name(self) -> str:
        return self._body.get('spec', {}).get('pod-selector', {}).get('matchLabels', {}).get('app')

    @template_name.setter
    def template_name(self, value: str):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        if not self._body.get('spec').get('pod-selector'):
            self._body['spec']['pod-selector'] = {}
        if not self._body.get('spec').get('pod-selector').get('matchLabels'):
            self._body['spec']['pod-selector']['matchLabels'] = {}
        self._body['spec']['pod-selector']['matchLabels']['app'] = value
        self._fields_to_update.add('spec.pod-selector.matchLabels.app')

    @property
    def start_timestamp(self) -> str:
        return self._body.get('spec', {}).get('start-time')

    @start_timestamp.setter
    def start_timestamp(self, value: str):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['start-time'] = str(value)
        self._fields_to_update.add('spec.start-time')

    @property
    def end_timestamp(self) -> str:
        return self._body.get('spec', {}).get('end-time')

    @end_timestamp.setter
    def end_timestamp(self, value: str):
        if not self._body.get('spec'):
            self._body['spec'] = {}
        self._body['spec']['end-time'] = str(value)
        self._fields_to_update.add('spec.end-time')

    @property
    def duration(self) -> Optional[str]:
        if self.end_timestamp and self.start_timestamp:
            return parser.parse(self.end_timestamp) - parser.parse(self.start_timestamp)
        elif self.start_timestamp:
            return datetime.now(timezone.utc) - parser.parse(self.start_timestamp)
        else:
            return None

    async def get_pods(self) -> List[V1Pod]:
        api = await K8SApiClient.get()
        try:
            pods = await api.list_namespaced_pod(label_selector=f'runName={self.name}',
                                                 namespace=self.namespace)
            return pods.items
        except ApiException as e:
            if e.status != HTTPStatus.NOT_FOUND:
                raise

    async def calculate_current_state(self) -> RunStatus:
        # Check final statuses first
        if self.state in {RunStatus.COMPLETE, RunStatus.FAILED, RunStatus.CANCELLED}:
            return self.state

        pods = await self.get_pods()

        if pods and any(pod.status.phase == 'Failed' for pod in pods):
            return RunStatus.FAILED
        elif not pods or (pods and any(pod.status.phase in {'Pending', 'Unknown'} for pod in pods)
                          and self.state is not RunStatus.RUNNING):
            return RunStatus.QUEUED
        elif pods and all(pod.status.phase == 'Succeeded' for pod in pods):
            return RunStatus.COMPLETE
        else:
            return RunStatus.RUNNING
