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

import re

from kubernetes import client
from marshmallow import Schema, fields, post_load, post_dump, validates, ValidationError
from cli_text_consts import PlatformResourcesCustomModelTexts as Texts


# kubernetes name requirements
KUBERNETES_NAME_RE = re.compile(r'[a-z]([-.a-z0-9]*[a-z0-9])?')


def validate_kubernetes_name(name: str):
    match = KUBERNETES_NAME_RE.fullmatch(name)
    if not match:
        raise ValidationError(Texts.INVALID_K8S_NAME)


class V1ObjectMetaSchema(Schema):
    annotations = fields.Dict(required=False, allow_none=True, missing=None)
    cluster_name = fields.String(required=False, allow_none=True, missing=None, dump_to='clusterName', load_from='clusterName')
    creation_timestamp = fields.DateTime(required=False, allow_none=True, missing=None, dump_to='creationTimestamp', load_from='creationTimestamp')
    deletion_grace_period_seconds = fields.Int(required=False, allow_none=True, missing=None, dump_to='deletionGracePeriodSeconds', load_from='deletionGracePeriodSeconds')
    deletion_timestamp = fields.DateTime(required=False, allow_none=True, missing=None, dump_to='deletionTimestamp', load_from='deletionTimestamp')
    finalizers = fields.List(fields.String, required=False, allow_none=True, missing=None)
    generate_name = fields.String(required=False, allow_none=True, missing=None, dump_to='generateName', load_from='generateName')
    generation = fields.Int(required=False, allow_none=True, missing=None)
    initializers = fields.Dict(required=False, allow_none=True, missing=None) # V1Initializers
    labels = fields.Dict(required=False, allow_none=True, missing=None)
    name = fields.String(required=True, allow_none=False)
    namespace = fields.String(required=True, allow_none=False)
    owner_references = fields.List(fields.Dict, required=False, allow_none=True, missing=None, dump_to='ownerReferences', load_from='ownerReferences') # list[V1OwnerReference]
    resource_version = fields.String(required=False, allow_none=True, missing=None, dump_to='resourceVersion', load_from='resourceVersion')
    self_link = fields.String(required=False, allow_none=True, missing=None, dump_to='selfLink', load_from='selfLink')
    uid = fields.String(required=False, allow_none=True, missing=None)

    @post_load
    def make_V1ObjectMeta(self, data):
        return client.V1ObjectMeta(**data)

    @post_dump
    def remove_none_value_fields(self, data):
        result = data.copy()
        for key in filter(lambda key: data[key] is None, data):
            del result[key]
        return result

    @validates('name')
    def validate_name(self, name: str):
        validate_kubernetes_name(name)
