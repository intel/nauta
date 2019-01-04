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

import http
from typing import Dict

import yaml
from kubernetes import client, config
from collections import namedtuple

from kubernetes.client import CustomObjectsApi
from kubernetes.client.rest import ApiException
from marshmallow import Schema, fields, post_load
from platform_resources.custom_object_meta_model import V1ObjectMetaSchema
from util.logger import initialize_logger

logger = initialize_logger(__name__)


class KubernetesObject(object):
    def __init__(self, spec, metadata: client.V1ObjectMeta, apiVersion: str='aipg.intel.com/v1',
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


class PlatformResourceApiClient:
    """
    This class is responsible for initializing default API client that will be used by PlatformResource class.
    If API client was already initialized, it will be returned by get() class method instead of creating a new client.
    """
    k8s_custom_object_api: CustomObjectsApi = None

    @classmethod
    def get(cls) -> CustomObjectsApi:
        if cls.k8s_custom_object_api:
            return cls.k8s_custom_object_api
        else:
            try:
                config.load_kube_config()
                k8s_custom_object_api = client.CustomObjectsApi(client.ApiClient())
                cls.k8s_custom_object_api = k8s_custom_object_api
                return cls.k8s_custom_object_api
            except Exception:
                logger.exception(f'Failed to initialize {cls.__name__}')


class PlatformResource:
    """
    Class representing any platform resource in form of Kubernetes CRD
    """
    api_group_name: str = None
    crd_plural_name: str = None
    crd_version: str = None

    def __init__(self, body: dict = None, name: str = None, namespace: str = None,
                 creation_timestamp: str = None, k8s_custom_object_api: CustomObjectsApi = None):
        self.body = body
        self.name = name
        self.namespace = namespace
        self.creation_timestamp = creation_timestamp
        self.k8s_custom_object_api = k8s_custom_object_api if k8s_custom_object_api else PlatformResourceApiClient.get()

    def __repr__(self):
        def format_field_value(value):
            return f'"{value}"' if type(value) == str else value

        fields =  ', '.join(['{key}={value}'.format(key=key, value=format_field_value(value))
                             for key, value in self.__dict__.items()])
        return '{class_name}({fields})'.format(class_name=self.__class__.__name__,
                                               fields=fields)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return {k: v for k,v in self.__dict__.items() if k != 'k8s_custom_object_api'} ==\
                   {k: v for k,v in other.__dict__.items() if k != 'k8s_custom_object_api'}
        return False

    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict):
        raise NotImplementedError

    @classmethod
    def from_yaml(cls, yaml_template_path: str):
        with open(yaml_template_path, mode='r', encoding='utf-8') as yaml_template_file:
            resource_body = yaml.safe_load(yaml_template_file)
        return cls(body=resource_body)

    @classmethod
    def list(cls, namespace: str = None, custom_objects_api: CustomObjectsApi = None):
        logger.debug(f'Getting list of {cls.__name__}s.')
        k8s_custom_object_api = custom_objects_api if custom_objects_api else PlatformResourceApiClient.get()
        if namespace:
            raw_resources = k8s_custom_object_api.list_namespaced_custom_object(group=cls.api_group_name,
                                                                                namespace=namespace,
                                                                                plural=cls.crd_plural_name,
                                                                                version=cls.crd_version)
        else:
            raw_resources = k8s_custom_object_api.list_cluster_custom_object(group=cls.api_group_name,
                                                                             plural=cls.crd_plural_name,
                                                                             version=cls.crd_version)

        return [cls.from_k8s_response_dict(raw_resource) for raw_resource in raw_resources['items']]

    @classmethod
    def get(cls, name: str, namespace: str = None, custom_objects_api: CustomObjectsApi = None):
        logger.debug(f'Getting {cls.__name__} {name} in namespace {namespace}.')
        k8s_custom_object_api = custom_objects_api if custom_objects_api else PlatformResourceApiClient.get()
        try:
            if namespace:
                raw_object = k8s_custom_object_api.get_namespaced_custom_object(group=cls.api_group_name,
                                                                                namespace=namespace,
                                                                                plural=cls.crd_plural_name,
                                                                                version=cls.crd_version,
                                                                                name=name)
            else:
                raw_object = k8s_custom_object_api.get_cluster_custom_object(group=cls.api_group_name,
                                                                             plural=cls.crd_plural_name,
                                                                             version=cls.crd_version,
                                                                             name=name)

        except ApiException as e:
            logger.exception(f'Failed to find {cls.__name__} {name} in namespace {namespace}.')
            if e.status == http.HTTPStatus.NOT_FOUND:
                raw_object = None
            else:
                raise

        return cls.from_k8s_response_dict(raw_object) if raw_object else None

    @property
    def cli_representation(self) -> namedtuple:
        raise NotImplementedError

    def create(self, namespace: str, labels: Dict[str, str] = None,
               annotations: Dict[str, str] = None):
        logger.debug(f'Creating {self.__class__.__name__} {self.name}.')
        try:
            if labels:
                self.body['metadata']['labels'] = labels
            if annotations:
                self.body['metadata']['annotations'] = annotations
            response = self.k8s_custom_object_api.create_namespaced_custom_object(group=self.api_group_name,
                                                                                  namespace=namespace,
                                                                                  body=self.body,
                                                                                  plural=self.crd_plural_name,
                                                                                  version=self.crd_version)
            self.name = response['metadata']['name']
            self.namespace = response['metadata']['namespace']
            return response
        except ApiException:
            logger.exception(f'Failed to create {self.__class__.__name__} {self.name}.')
            raise

    def delete(self) -> KubernetesObject:
        if not self.name:
            raise RuntimeError(f'{self.__class__.__name__} has not been created.')

        logger.debug(f'Deleting {self.__class__.__name__} {self.name}.')

        try:
            response = self.k8s_custom_object_api.delete_namespaced_custom_object(group=self.api_group_name,
                                                                                  namespace=self.namespace,
                                                                                  plural=self.crd_plural_name,
                                                                                  version=self.crd_version,
                                                                                  name=self.name, body={})
            return response
        except ApiException:
            logger.exception(f'Failed to delete {self.__class__.__name__} {self.name}.')
            raise

    def update(self):
        logger.debug(f'Updating {self.__class__.__name__} {self.name}.')
        try:
            response = self.k8s_custom_object_api.patch_namespaced_custom_object(group=self.api_group_name,
                                                                                 namespace=self.namespace,
                                                                                 body=self.body,
                                                                                 plural=self.crd_plural_name,
                                                                                 version=self.crd_version,
                                                                                 name=self.name)
            return response
        except ApiException:
            logger.exception(f'Failed to update {self.__class__.__name__} {self.name}.')
            raise
