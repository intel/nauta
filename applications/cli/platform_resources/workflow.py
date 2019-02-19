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

from collections import namedtuple

from kubernetes.client import CustomObjectsApi

from platform_resources.platform_resource import PlatformResource


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
    def from_k8s_response_dict(cls, object_dict: dict):
        return cls(name=object_dict['metadata'].get('name'),
                   namespace=object_dict['metadata'].get('namespace'),
                   started_at=object_dict.get('status', {}).get('startedAt'),
                   finished_at=object_dict.get('status', {}).get('finishedAt'),
                   status=object_dict.get('status', {}),
                   phase=object_dict.get('status', {}).get('phase'))

    @property
    def cli_representation(self):
        return ArgoWorkflow.ArgoWorkflowCliModel(name=self.name,
                                                 started_at=self.started_at,
                                                 finished_at=self.finished_at,
                                                 submitter=self.namespace,
                                                 phase=self.phase)
