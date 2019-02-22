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
import dateutil
from enum import Enum
from typing import List, Optional

from kubernetes.client import CustomObjectsApi

from platform_resources.platform_resource import PlatformResource, PlatformResourceApiClient
from platform_resources.run import Run, RunStatus
from util.logger import initialize_logger
from util.system import format_timestamp_for_cli

logger = initialize_logger(__name__)

class UserStatus(Enum):
    DEFINED = 'DEFINED'
    CREATED = 'CREATED'
    UNKNOWN = 'UNKNOWN'


class User(PlatformResource):
    api_group_name = 'aipg.intel.com'
    crd_plural_name = 'users'
    crd_version = 'v1'

    UserCliModel = namedtuple('UserCliModel', ['name', 'created', 'date_of_last_submitted_job',
                                               'running_jobs', 'queued_jobs'])

    def __init__(self, name: str, uid: int, state: UserStatus = UserStatus.DEFINED,
                 creation_timestamp: str = None, experiment_runs: List[Run] = None):
        super().__init__()
        self.name = name
        self.uid = uid
        self.state = state
        self.creation_timestamp = creation_timestamp
        self.experiment_runs = experiment_runs if experiment_runs else []


    @classmethod
    def from_k8s_response_dict(cls, object_dict: dict):
        name = "---"
        uid = "---"
        state = UserStatus.UNKNOWN
        creation_timestamp = "---"

        if object_dict:
            if object_dict.get('metadata'):
                    name = object_dict.get('metadata').get('name')
                    creation_timestamp = object_dict.get('metadata').get('creationTimestamp')

            if object_dict.get('spec'):
                uid = object_dict.get('spec').get('uid')

                if object_dict.get('spec').get('state'):
                    state = UserStatus[object_dict.get('spec').get('state')]

        return cls(name=name,
                   uid=uid,
                   state=state,
                   creation_timestamp=creation_timestamp)

    @classmethod
    def list(cls, namespace: str = None, custom_objects_api: CustomObjectsApi = None):
        """
        Return list of users.
        :namespace:
        :return: List of User objects
        """
        logger.debug('Listing users.')
        k8s_custom_object_api = custom_objects_api if custom_objects_api else PlatformResourceApiClient.get()

        raw_users = k8s_custom_object_api.list_cluster_custom_object(group=cls.api_group_name,
                                                                     plural=cls.crd_plural_name,
                                                                     version=cls.crd_version)

        users = [User.from_k8s_response_dict(user_dict) for user_dict in raw_users['items']]

        # Get experiment runs for each user
        # TODO: CHANGE IMPLEMENTATION TO USE AGGREGATED USER DATA AFTER CAN-366
        runs = Run.list(custom_objects_api=k8s_custom_object_api)
        user_map = {user.name: user for user in users}

        for run in runs:
            if user_map.get(run.namespace):
                user_map[run.namespace].experiment_runs.append(run)
            else:
                logger.error(f"Run exists for nonexisting user {run.namespace}")

        return users

    @property
    def cli_representation(self):
        return User.UserCliModel(name=self.name, created=format_timestamp_for_cli(self.creation_timestamp),
                                 running_jobs=self.running_jobs_count, queued_jobs=self.queued_jobs_count,
                                 date_of_last_submitted_job=format_timestamp_for_cli(self.date_of_last_submitted_job)
                                                            if self.date_of_last_submitted_job is not None else None)

    @property
    def date_of_last_submitted_job(self) -> Optional[str]:
        if self.experiment_runs:
            return sorted((run for run in self.experiment_runs),
                          key=lambda run: dateutil.parser.parse(run.creation_timestamp))[-1].creation_timestamp
        else:
            return None

    @property
    def running_jobs_count(self) -> int:
        return len([run for run in self.experiment_runs if run.state == RunStatus.RUNNING])

    @property
    def queued_jobs_count(self) -> int:
        return len([run for run in self.experiment_runs if run.state == RunStatus.QUEUED])
