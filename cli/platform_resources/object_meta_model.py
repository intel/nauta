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

from kubernetes import client
from marshmallow import Schema, fields, post_load, post_dump


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
