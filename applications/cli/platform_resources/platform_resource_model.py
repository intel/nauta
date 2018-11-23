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

from abc import ABC
from kubernetes import client
from collections import namedtuple
from marshmallow import Schema, fields, post_load, validates
from marshmallow_enum import EnumField
from platform_resources.custom_object_meta_model import V1ObjectMetaSchema, validate_kubernetes_name

class PlatformResource(ABC):
    submitter: str
    creation_timestamp: str

    def __repr__(self):
        def format_field_value(value):
            return f'"{value}"' if type(value) == str else value

        fields =  ', '.join(['{key}={value}'.format(key=key, value=format_field_value(value))
                             for key, value in self.__dict__.items()])
        return '{class_name}({fields})'.format(class_name=self.__class__.__name__,
                                               fields=fields)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict):
        raise NotImplementedError

    @property
    def cli_representation(self) -> namedtuple:
        raise NotImplementedError


class KubernetesObject(object):
    def __init__(self, spec: PlatformResource, metadata: client.V1ObjectMeta, apiVersion: str='aipg.intel.com/v1',
                 kind: str='') -> None:
        self.apiVersion = apiVersion
        self.kind = kind
        self.metadata = metadata
        self.spec = spec


class KubernetesObjectSchema(Schema):
    apiVersion = fields.String(required=True, allow_none=False)
    kind = fields.String(required=True, allow_none=False)
    metadata = fields.Nested(V1ObjectMetaSchema(), required=True, allow_none=False)
    spec = fields.Raw(allow_none=True)

    @post_load
    def make_kubernetes_object(self, data):
        return KubernetesObject(**data)
