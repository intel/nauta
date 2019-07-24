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
from datetime import datetime, timezone
from dateutil import parser
from enum import Enum
import re
import sre_constants
import textwrap
from functools import partial
from typing import List, Tuple, Dict

from kubernetes.client import CustomObjectsApi
from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from cli_text_consts import PlatformResourcesExperimentsTexts as Texts
from platform_resources.platform_resource import PlatformResource, KubernetesObjectSchema, KubernetesObject, client, \
    PlatformResourceApiClient
from platform_resources.resource_filters import filter_by_name_regex, filter_by_experiment_name
from util.exceptions import InvalidRegularExpressionError
from util.logger import initialize_logger
from util.system import format_timestamp_for_cli, format_duration_for_cli


logger = initialize_logger(__name__)


class RunKinds(Enum):
    """ This enum contains all allowed run kinds which are used to filter runs in "list" commands. """
    TRAINING = "training"
    JUPYTER = "jupyter"
    INFERENCE = "inference"


class RunStatus(Enum):
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    COMPLETE = 'COMPLETE'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'
    # state taken from an experiment - CAN-732
    CREATING = 'CREATING'


class Run(PlatformResource):
    api_group_name = 'aggregator.aipg.intel.com'
    crd_plural_name = 'runs'
    crd_version = 'v1'

    RunCliModel = namedtuple('RunCliModel', ['name', 'parameters', 'metrics',
                                             'submission_date', 'start_date', 'duration', 'submitter', 'status',
                                             'template_name', 'template_version'])

    def __init__(self, name: str, experiment_name: str, metrics: dict = None, parameters: Tuple[str, ...] = None,
                 pod_count: int = None, pod_selector: dict = None,
                 state: RunStatus = None, namespace: str = None,
                 creation_timestamp: str = None, template_name: str = None, metadata: dict = None,
                 start_timestamp: str = None, end_timestamp: str = None, template_version: str = None):
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.state = state
        self.metrics = metrics
        self.experiment_name = experiment_name
        self.pod_count = pod_count
        self.pod_selector = pod_selector
        self.namespace = namespace
        self.creation_timestamp = creation_timestamp
        self.template_name = template_name
        self.metadata = metadata
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        if end_timestamp and start_timestamp:
            self.duration = parser.parse(end_timestamp) - parser.parse(start_timestamp)
        elif start_timestamp:
            self.duration = datetime.now(timezone.utc) - parser.parse(start_timestamp)
        else:
            self.duration = None
        self.template_version = template_version

    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict):
        run_state = object_dict.get('spec', {}).get('state')
        return cls(name=object_dict['metadata']['name'],
                   parameters=object_dict.get('spec', {}).get('parameters'),
                   creation_timestamp=object_dict.get('metadata', {}).get('creationTimestamp'),
                   namespace=object_dict.get('metadata', {}).get('namespace'),
                   state=RunStatus[run_state] if run_state else RunStatus.CREATING,
                   pod_count=object_dict.get('spec', {}).get('pod-count'),
                   pod_selector=object_dict.get('spec', {}).get('pod-selector'),
                   experiment_name=object_dict.get('spec', {}).get('experiment-name'),
                   metrics=object_dict.get('spec', {}).get('metrics', {}),
                   template_name=object_dict.get('spec', {}).get('pod-selector', {}).get('matchLabels', {}).get('app'),
                   metadata=object_dict.get('metadata'),
                   start_timestamp=object_dict.get('spec', {}).get('start-time'),
                   end_timestamp=object_dict.get('spec', {}).get('end-time'))

    @classmethod
    def list(cls, namespace: str = None, custom_objects_api: CustomObjectsApi = None, **kwargs):
        """
        Return list of experiment runs.
        :param namespace: If provided, only runs from this namespace will be returned
        :param state_list: If provided, only runs with given states will be returned
        :param name_filter: If provided, only runs matching name_filter regular expression will be returned
        :param exp_name_filter: If provided, list of runs is filtered by experiment names from given list
        :param excl_state: If provided, only runs with a state other than given will be returned
        :param run_kinds_filter: If provided, only runs with a kind that matches to any of the run kinds from given
            filtering list will be returned
        :return: List of Run objects
        In case of problems during getting a list of runs - throws an error
        """
        state_list = kwargs.pop('state_list', None)
        name_filter = kwargs.pop('name_filter', None)
        exp_name_filter = kwargs.pop('exp_name_filter', None)
        excl_state = kwargs.pop('excl_state', None)
        run_kinds_filter = kwargs.pop('run_kinds_filter', None)
        
        k8s_custom_object_api = custom_objects_api if custom_objects_api else PlatformResourceApiClient.get()
        if namespace:
            raw_runs = k8s_custom_object_api.list_namespaced_custom_object(group=Run.api_group_name,
                                                                           namespace=namespace,
                                                                           plural=Run.crd_plural_name,
                                                                           version=Run.crd_version)
        else:
            raw_runs = k8s_custom_object_api.list_cluster_custom_object(group=Run.api_group_name,
                                                                        plural=Run.crd_plural_name,
                                                                        version=Run.crd_version)

        try:
            name_regex = re.compile(name_filter) if name_filter else None
        except sre_constants.error as e:
            error_msg = Texts.REGEX_COMPILATION_FAIL_MSG.format(name_filter=name_filter)
            logger.exception(error_msg)
            raise InvalidRegularExpressionError(error_msg) from e

        run_filters = [partial(filter_by_name_regex, name_regex=name_regex, spec_location=False),
                       partial(filter_run_by_state, state_list=state_list),
                       partial(filter_run_by_excl_state, state=excl_state),
                       partial(filter_by_experiment_name, exp_name=exp_name_filter),
                       partial(filter_by_run_kinds, run_kinds=run_kinds_filter)]

        runs = [Run.from_k8s_response_dict(run_dict)
                for run_dict in raw_runs['items']
                if all(f(run_dict) for f in run_filters)]
        return runs

    @property
    def cli_representation(self):
        return Run.RunCliModel(name=self.name,
                               parameters=textwrap.fill(' '.join(self.parameters), width=30,
                                                        drop_whitespace=False) if self.parameters else "",
                               metrics='\n'.join(textwrap.fill(f'{key}: {value}', width=30)
                                                 for key, value in self.metrics.items()) if self.metrics else "",
                               submission_date=format_timestamp_for_cli(self.creation_timestamp) if self.creation_timestamp else "",
                               submitter=self.namespace if self.namespace else "",
                               status=self.state.value if self.state else "",
                               template_name=self.template_name,
                               start_date=format_timestamp_for_cli(self.start_timestamp) if self.start_timestamp else "",
                               duration=format_duration_for_cli(self.duration) if self.duration else "",
                               template_version=self.template_version)

    def create(self, namespace: str, labels: Dict[str, str] = None, annotations: Dict[str, str] = None):
        run_kubernetes = KubernetesObject(self, client.V1ObjectMeta(name=self.name, namespace=namespace, labels=labels,
                                                                    annotations=annotations),
                                          kind="Run", apiVersion=f"{self.api_group_name}/{self.crd_version}")
        schema = RunKubernetesSchema()
        body, err = schema.dump(run_kubernetes)
        if err:
            raise RuntimeError(f'preparing dump of RunKubernetes request object error - {err}')
        self.body = body

        response = super().create(namespace=namespace)
        created_run, err = schema.load(response)
        if err:
            raise RuntimeError(f'load of RunKubernetes request object error - {err}')
        return created_run

    def update(self):
        run_kubernetes = KubernetesObject(self, client.V1ObjectMeta(name=self.name, namespace=self.namespace),
                                          kind="Run", apiVersion=f"{self.api_group_name}/{self.crd_version}")
        schema = RunKubernetesSchema()
        body, err = schema.dump(run_kubernetes)
        if err:
            raise RuntimeError(f'preparing dump of RunKubernetes request object error - {err}')
        self.body = body

        response = super().update()
        updated_run, err = schema.load(response)
        if err:
            raise RuntimeError(f'load of RunKubernetes request object error - {err}')
        return updated_run


class RunSchema(Schema):
    name = fields.String(required=True, allow_none=False, load_from='experiment-name')
    experiment_name = fields.String(required=True, allow_none=False, dump_to='experiment-name',
                                    load_from='experiment-name')
    parameters = fields.List(fields.String, required=False, missing=None, allow_none=True)
    metrics = fields.Dict(fields.String, required=False, missing=None, allow_none=True)
    pod_count = fields.Int(required=False, missing=None, allow_none=True, dump_to='pod-count', load_from='pod-count')
    pod_selector = fields.Dict(fields.String, required=False, missing=None, allow_none=True, dump_to='pod-selector',
                               load_from='pod-selector')
    state = EnumField(RunStatus, required=True, allow_none=False, by_value=True)

    @post_load
    def make_run(self, data):
        result = Run(**data)
        result.template_name = result.pod_selector['matchLabels']['app']
        return result


class RunKubernetesSchema(KubernetesObjectSchema):
    spec = fields.Nested(RunSchema(), required=True, allow_none=False)


def filter_run_by_state(resource_object_dict: dict, state_list: List[Enum] = None):
    if not state_list or not all(state_list):
        return True

    current_state = resource_object_dict['spec'].get('state')
    if current_state:
        if [item for item in state_list if item.value == current_state]:
            return True
        else:
            return False
    else:
        if state_list and state_list[0] == RunStatus.CREATING:
            return True
        else:
            return False


def filter_run_by_excl_state(resource_object_dict: dict, state: Enum = None):
    if not state:
        return True

    return not filter_run_by_state(resource_object_dict, [state])


def filter_by_run_kinds(resource_object_dict: dict, run_kinds: List[Enum] = None):
    return any([resource_object_dict['metadata']['labels'].get('runKind') == run_kind.value for run_kind in run_kinds]) \
        if run_kinds else True