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

from collections import namedtuple
from enum import Enum
import textwrap
from typing import List
from marshmallow import Schema, fields, post_load, validates
from marshmallow_enum import EnumField

from platform_resources.platform_resource_model import PlatformResource, KubernetesObjectSchema
from util.system import format_timestamp_for_cli


class RunStatus(Enum):
    QUEUED = 'QUEUED'
    RUNNING = 'RUNNING'
    COMPLETE = 'COMPLETE'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'
    # state taken from an experiment - CAN-732
    CREATING = 'CREATING'



class Run(PlatformResource):
    RunCliModel = namedtuple('RunCliModel', ['name', 'parameters', 'metrics',
                                             'submission_date', 'submitter', 'status', 'template_name'])

    def __init__(self, name: str, experiment_name: str, metrics: dict, parameters: List[str],
                 pod_count: int, pod_selector: dict, state: RunStatus, submitter: str = None,
                 creation_timestamp: str = None, template_name: str = None):
        self.name = name
        self.parameters = parameters
        self.state = state
        self.metrics = metrics
        self.experiment_name = experiment_name
        self.pod_count = pod_count
        self.pod_selector = pod_selector
        self.submitter = submitter
        self.creation_timestamp = creation_timestamp
        self.template_name = template_name


    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict):
        return cls(name=object_dict['metadata']['name'],
                   parameters=object_dict.get('spec').get('parameters'),
                   creation_timestamp=object_dict['metadata']['creationTimestamp'],
                   submitter=object_dict['metadata']['namespace'],
                   state=RunStatus[object_dict['spec']['state']] if 'state' in object_dict['spec'] else "",
                   pod_count=object_dict['spec']['pod-count'],
                   pod_selector=object_dict['spec']['pod-selector'],
                   experiment_name=object_dict['spec']['experiment-name'],
                   metrics=object_dict['spec']['metrics'],
                   template_name=object_dict['spec']['pod-selector']['matchLabels']['app'])

    @property
    def cli_representation(self):
        return Run.RunCliModel(name=self.name,
                               parameters=textwrap.fill(' '.join(self.parameters), width=30) if self.parameters else "",
                               metrics=textwrap.fill(
                                   ' '.join(f'{key}: {value}' for key, value in self.metrics.items()),
                                   width=30),
                               submission_date=format_timestamp_for_cli(self.creation_timestamp),
                               submitter=self.submitter,
                               status=self.state.value if self.state else "",
                               template_name=self.template_name)


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
