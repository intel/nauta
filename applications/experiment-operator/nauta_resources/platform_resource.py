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
from typing import Dict, List, Optional, TypeVar
import logging

import dpath.util
import yaml
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client import CustomObjectsApi, CoreV1Api
from kubernetes_asyncio.client.rest import ApiException

logger = logging.getLogger(__name__)


class K8SApiClient:
    """
    This class is responsible for initializing default API client singleton.
    If API client was already initialized, it will be returned by get() class method instead of creating a new client.
    """
    core_api: CoreV1Api = None

    @classmethod
    async def get(cls) -> CoreV1Api:
        if cls.core_api:
            return cls.core_api
        else:
            try:
                try:
                    await config.load_kube_config()
                except FileNotFoundError:
                    config.load_incluster_config()

                cls.core_api = client.CoreV1Api(client.ApiClient())
                return cls.core_api
            except Exception:
                logger.exception(f'Failed to initialize {cls.__name__}')
                raise


class CustomResourceApiClient:
    """
    This class is responsible for initializing default Custom Resource API client singleton.
    If API client was already initialized, it will be returned by get() class method instead of creating a new client.
    """
    k8s_custom_object_api: CustomObjectsApi = None

    @classmethod
    async def get(cls) -> CustomObjectsApi:
        if cls.k8s_custom_object_api:
            return cls.k8s_custom_object_api
        else:
            try:
                try:
                    await config.load_kube_config()
                except FileNotFoundError:
                    config.load_incluster_config()

                cls.k8s_custom_object_api = client.CustomObjectsApi(client.ApiClient())
                return cls.k8s_custom_object_api
            except Exception:
                logger.exception(f'Failed to initialize {cls.__name__}')
                raise


CustomResourceTypeVar = TypeVar('CustomResourceTypeVar', bound='CustomResource')


class CustomResource:
    """
    Class representing any platform resource in form of Kubernetes CRD, intended to be subclassed.
    In the subclass, provide values for api_group_name, crd_plural_name and crd_version class fields.
    """
    api_group_name: str
    crd_plural_name: str
    crd_version: str

    def __init__(self, body: dict = None, name: str = None, namespace: str = None):
        # self._fields_to_update keeps list of json fields that should be patched when calling self.update()
        # it is assumed that each property setter will properly update this set
        self._fields_to_update = set()
        
        self._body = body
        self.name = name
        self.namespace = namespace

    @property
    def metadata(self) -> dict:
        return self._body.get('metadata')

    @metadata.setter
    def metadata(self, value: dict):
        self._body['metadata'] = value
        self._fields_to_update.add('metadata')

    @property
    def creation_timestamp(self) -> str:
        return self._body.get('metadata', {}).get('creationTimestamp')

    @creation_timestamp.setter
    def creation_timestamp(self, value: str):
        if not self._body.get('metadata'):
            self._body['metadata'] = {}
        self._body['metadata']['creationTimestamp'] = value
        self._fields_to_update.add('metadata.creationTimestamp')

    def __repr__(self):
        def format_field_value(value):
            return f'"{value}"' if type(value) == str else value

        fields = ', '.join(['{key}={value}'.format(key=key, value=format_field_value(value))
                            for key, value in self.__dict__.items()])
        return '{class_name}({fields})'.format(class_name=self.__class__.__name__,
                                               fields=fields)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return {k: v for k, v in self.__dict__.items()} == {k: v for k, v in other.__dict__.items()}
        return False

    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict) -> CustomResourceTypeVar:
        # Fields below should be opaque to the client, so we simply remove them
        try:
            del object_dict['metadata']['generation']
            del object_dict['metadata']['resourceVersion']
        except KeyError:
            pass
        return cls(name=object_dict['metadata']['name'],
                   body=object_dict,
                   namespace=object_dict.get('metadata', {}).get('namespace'))

    @classmethod
    def from_yaml(cls, yaml_template_path: str, *args, **kwargs) -> CustomResourceTypeVar:
        with open(yaml_template_path, mode='r', encoding='utf-8') as yaml_template_file:
            resource_body = yaml.safe_load(yaml_template_file)
        kwargs.pop('body', None)
        return cls(body=resource_body, *args, **kwargs)

    @classmethod
    async def list(cls, namespace: str = None, label_selector: str = None, **kwargs) -> List[CustomResourceTypeVar]:
        logger.debug(f'Getting list of {cls.__name__}s.')
        k8s_custom_object_api = await CustomResourceApiClient.get()
        if namespace:
            raw_resources = await k8s_custom_object_api.list_namespaced_custom_object(group=cls.api_group_name,
                                                                                      namespace=namespace,
                                                                                      plural=cls.crd_plural_name,
                                                                                      version=cls.crd_version,
                                                                                      label_selector=label_selector)
        else:
            raw_resources = await k8s_custom_object_api.list_cluster_custom_object(group=cls.api_group_name,
                                                                                   plural=cls.crd_plural_name,
                                                                                   version=cls.crd_version,
                                                                                   label_selector=label_selector)

        return [cls.from_k8s_response_dict(raw_resource) for raw_resource in raw_resources['items']]

    @classmethod
    async def get(cls, name: str, namespace: str = None) -> Optional[CustomResourceTypeVar]:
        logger.debug(f'Getting {cls.__name__} {name} in namespace {namespace}.')
        k8s_custom_object_api = await CustomResourceApiClient.get()
        try:
            if namespace:
                raw_object = await k8s_custom_object_api.get_namespaced_custom_object(group=cls.api_group_name,
                                                                                      namespace=namespace,
                                                                                      plural=cls.crd_plural_name,
                                                                                      version=cls.crd_version,
                                                                                      name=name)
            else:
                raw_object = await k8s_custom_object_api.get_cluster_custom_object(group=cls.api_group_name,
                                                                                   plural=cls.crd_plural_name,
                                                                                   version=cls.crd_version,
                                                                                   name=name)

        except ApiException as e:
            if e.status == http.HTTPStatus.NOT_FOUND:
                logger.debug(f'Failed to find {cls.__name__} {name} in namespace {namespace}.')
                raw_object = None
            else:
                logger.exception(f'The error {e.status} has been returned while getting {cls.__name__} '
                                 f'{name} object in namespace {namespace}.')
                raise

        return cls.from_k8s_response_dict(raw_object) if raw_object else None

    @property
    def labels(self) -> Dict[str, str]:
        return self._body.get('metadata', {}).get('labels', {})

    @labels.setter
    def labels(self, value: Dict[str, str]):
        if not self._body.get('metadata'):
            self._body['metadata'] = {}
        self._body['metadata']['labels'] = value

    async def create(self, namespace: str, labels: Dict[str, str] = None,
                     annotations: Dict[str, str] = None):
        logger.debug(f'Creating {self.__class__.__name__} {self.name}.')
        k8s_custom_object_api = await CustomResourceApiClient.get()
        try:
            if labels:
                self._body['metadata']['labels'] = labels
            if annotations:
                self._body['metadata']['annotations'] = annotations
            response = await k8s_custom_object_api.create_namespaced_custom_object(group=self.api_group_name,
                                                                                   namespace=namespace,
                                                                                   body=self._body,
                                                                                   plural=self.crd_plural_name,
                                                                                   version=self.crd_version)
            self.name = response['metadata']['name']
            self.namespace = response['metadata']['namespace']
            return response
        except ApiException:
            logger.exception(f'Failed to create {self.__class__.__name__} {self.name}.')
            raise

    async def delete(self):
        if not self.name:
            raise RuntimeError(f'{self.__class__.__name__} has not been created.')

        logger.debug(f'Deleting {self.__class__.__name__} {self.name}.')
        k8s_custom_object_api = await CustomResourceApiClient.get()

        try:
            response = await k8s_custom_object_api.delete_namespaced_custom_object(group=self.api_group_name,
                                                                                   namespace=self.namespace,
                                                                                   plural=self.crd_plural_name,
                                                                                   version=self.crd_version,
                                                                                   name=self.name, body={})
            return response
        except ApiException:
            logger.exception(f'Failed to delete {self.__class__.__name__} {self.name}.')
            raise

    async def update(self):
        logger.debug(f'Updating {self.__class__.__name__} {self.name}.')
        k8s_custom_object_api = await CustomResourceApiClient.get()

        patch_body = {}
        if self._fields_to_update:
            for field in self._fields_to_update:
                dpath.util.new(patch_body, field, dpath.util.get(self._body, field, separator='.'), separator='.')
            logger.debug(f'Patch body for {self.__class__.__name__} {self.name}: {patch_body}')
        else:
            logger.debug(f'No fields were changed in {self.__class__.__name__} {self.name}, skipping update.')
            return
        try:
            response = await k8s_custom_object_api.patch_namespaced_custom_object(group=self.api_group_name,
                                                                                  namespace=self.namespace,
                                                                                  body=patch_body,
                                                                                  plural=self.crd_plural_name,
                                                                                  version=self.crd_version,
                                                                                  name=self.name)
            self._fields_to_update = set()  # Clear after successful update
            return response
        except ApiException:
            logger.exception(f'Failed to update {self.__class__.__name__} {self.name}.')
            raise
