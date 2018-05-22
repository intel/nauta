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
from typing import List

from kubernetes import client
from marshmallow import Schema, fields, post_load, validates
from marshmallow_enum import EnumField

from platform_resources.custom_object_meta_model import V1ObjectMetaSchema, validate_kubernetes_name
from platform_resources.platform_resource_model import PlatformResource


class ExperimentStatus(Enum):
    CREATING = 'CREATING'
    SUBMITTED = 'SUBMITTED'
    FAILED = 'FAILED'


class Experiment(PlatformResource):

    ExperimentCliModel = namedtuple('Experiment', ['name', 'parameters_spec',
                                                   'creation_timestamp', 'submitter', 'status'])

    def __init__(self, name: str, template_name: str, template_namespace: str, parameters_spec: List[str]=None,
                 state: ExperimentStatus=ExperimentStatus.CREATING, creation_timestamp: str = None,
                 submitter: str = None):
        self.name = name
        self.parameters_spec = parameters_spec
        self.state = state
        self.template_name = template_name
        self.template_namespace = template_namespace
        self.creation_timestamp = creation_timestamp
        self.submitter = submitter

    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict):
        return cls(name=object_dict['spec']['name'],
                   parameters_spec=object_dict['spec']['parameters-spec'],
                   creation_timestamp=object_dict['metadata']['creationTimestamp'],
                   submitter=object_dict['metadata']['namespace'],
                   state=ExperimentStatus[object_dict['spec']['state']],
                   template_name=object_dict['spec']['template-name'],
                   template_namespace=object_dict['spec']['template-namespace'])

    @property
    def cli_representation(self):
        return Experiment.ExperimentCliModel(name=self.name, parameters_spec=' '.join(self.parameters_spec),
                                             creation_timestamp=self.creation_timestamp, submitter=self.submitter,
                                             status=self.state.value)


class ExperimentSchema(Schema):
    name = fields.String(required=True, allow_none=False)
    parameters_spec = fields.List(fields.String, required=False, missing=None, allow_none=True,
                                  dump_to='parameters-spec', load_from='parameters-spec')
    state = EnumField(ExperimentStatus, required=True, allow_none=False, by_value=True)
    template_name = fields.String(required=True, allow_none=False, dump_to='template-name', load_from='template-name')
    template_namespace = fields.String(required=True, allow_none=False, dump_to='template-namespace',
                                       load_from='template-namespace')

    @post_load
    def make_experiment(self, data):
        return Experiment(**data)

    @validates('name')
    def validate_name(self, name: str):
        validate_kubernetes_name(name)


class ExperimentKubernetes(object):
    def __init__(self, spec: Experiment, metadata: client.V1ObjectMeta, apiVersion: str='aipg.intel.com/v1', kind: str='Experiment') -> None:
        self.apiVersion = apiVersion
        self.kind = kind
        self.metadata = metadata
        self.spec = spec


class ExperimentKubernetesSchema(Schema):
    apiVersion = fields.String(required=True, allow_none=False)
    kind = fields.String(required=True, allow_none=False)
    spec = fields.Nested(ExperimentSchema(), required=True, allow_none=False)
    metadata = fields.Nested(V1ObjectMetaSchema(), required=True, allow_none=False)

    @post_load
    def make_experiment_kubernetes(self, data):
        return ExperimentKubernetes(**data)
