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

from hashlib import sha1
import os
from typing import List

from kubernetes import client as k8s
from nauta.config import NautaPlatformConfig
from tensorboard.models import Run


class K8STensorboardInstance:
    EXPERIMENTS_OUTPUT_VOLUME_NAME = 'output-public'
    TENSORBOARD_CONTAINER_MOUNT_PATH_PREFIX = '/mnt/exp'

    def __init__(self, deployment: k8s.V1Deployment, service: k8s.V1Service, ingress: k8s.V1beta1Ingress,
                 pod: k8s.V1Pod = None):
        self.deployment = deployment
        self.service = service
        self.ingress = ingress
        self.pod = pod

    @staticmethod
    def generate_run_names_hash(runs: List[Run]) -> str:
        run_names_condensed = []

        for run in runs:
            run_names_condensed.append(run.owner+":"+run.name)

        run_names_condensed.sort()
        run_names_str = ",".join(run_names_condensed)
        run_names_hash = sha1(run_names_str.encode('utf-8')).hexdigest()
        return run_names_hash

    @classmethod
    def from_runs(cls, id: str, runs: List[Run]):
        k8s_name = 'tensorboard-' + id
        run_names_hash = K8STensorboardInstance.generate_run_names_hash(runs)

        volume_mounts = []

        for run in runs:
            mount = k8s.V1VolumeMount(
                name=cls.EXPERIMENTS_OUTPUT_VOLUME_NAME,
                mount_path=os.path.join(cls.TENSORBOARD_CONTAINER_MOUNT_PATH_PREFIX, run.owner, run.name),
                sub_path=os.path.join(run.owner, run.name)
            )
            volume_mounts.append(mount)

        deployment_labels = {
            'name': k8s_name,
            'type': 'nauta-tensorboard',
            'nauta_app_name': 'tensorboard',
            'id': id,
            'runs-hash': run_names_hash
        }

        tensorboard_command = [
            "tensorboard",
            "--logdir", cls.TENSORBOARD_CONTAINER_MOUNT_PATH_PREFIX,
            "--port", "6006",
            "--host", "127.0.0.1"
        ]

        nauta_config = NautaPlatformConfig.incluster_init()

        tensorboard_image = nauta_config.get_tensorboard_image()
        tensorboard_proxy_image = nauta_config.get_activity_proxy_image()

        deployment = k8s.V1Deployment(api_version='apps/v1',
                                      kind='Deployment',
                                      metadata=k8s.V1ObjectMeta(
                                          name=k8s_name,
                                          labels=deployment_labels
                                      ),
                                      spec=k8s.V1DeploymentSpec(
                                          replicas=1,
                                          selector=k8s.V1LabelSelector(
                                              match_labels=deployment_labels
                                          ),
                                          template=k8s.V1PodTemplateSpec(
                                              metadata=k8s.V1ObjectMeta(
                                                  labels=deployment_labels
                                              ),
                                              spec=k8s.V1PodSpec(
                                                  tolerations=[k8s.V1Toleration(
                                                      key='master',
                                                      operator='Exists',
                                                      effect='NoSchedule'
                                                  )],
                                                  affinity=k8s.V1Affinity(
                                                      node_affinity=k8s.V1NodeAffinity(
                                                          required_during_scheduling_ignored_during_execution=
                                                          k8s.V1NodeSelector(node_selector_terms=
                                                          [k8s.V1NodeSelectorTerm(
                                                              match_expressions=[k8s.V1NodeSelectorRequirement(
                                                                  key="master",
                                                                  operator="In",
                                                                  values=["True"]
                                                              )]
                                                          )]
                                                          )
                                                      )
                                                  ),
                                                  containers=[
                                                      k8s.V1Container(
                                                          name='app',
                                                          image=tensorboard_image,
                                                          command=tensorboard_command,
                                                          volume_mounts=volume_mounts),
                                                      k8s.V1Container(
                                                          name='proxy',
                                                          image=tensorboard_proxy_image,
                                                          ports=[
                                                              k8s.V1ContainerPort(
                                                                  container_port=80
                                                              )
                                                          ],
                                                          readiness_probe=k8s.V1Probe(
                                                              period_seconds=5,
                                                              http_get=k8s.V1HTTPGetAction(
                                                                  path='/healthz',
                                                                  port=80
                                                              )
                                                          )
                                                      )
                                                  ],
                                                  volumes=[
                                                      k8s.V1Volume(
                                                          name=cls.EXPERIMENTS_OUTPUT_VOLUME_NAME,
                                                          persistent_volume_claim=  # noqa
                                                          k8s.V1PersistentVolumeClaimVolumeSource(
                                                              claim_name=cls.EXPERIMENTS_OUTPUT_VOLUME_NAME,
                                                              read_only=True
                                                          )
                                                      )
                                                  ]
                                              )
                                          )
                                      ))

        service = k8s.V1Service(api_version='v1',
                                kind='Service',
                                metadata=k8s.V1ObjectMeta(
                                    name=k8s_name,
                                    labels={
                                        'name': k8s_name,
                                        'type': 'nauta-tensorboard',
                                        'nauta_app_name': 'tensorboard',
                                        'id': id
                                    }
                                ),
                                spec=k8s.V1ServiceSpec(
                                    type='ClusterIP',
                                    ports=[
                                        k8s.V1ServicePort(
                                            name='web',
                                            port=80,
                                            target_port=80
                                        )
                                    ],
                                    selector={
                                        'name': k8s_name,
                                        'type': 'nauta-tensorboard',
                                        'nauta_app_name': 'tensorboard',
                                        'id': id
                                    }
                                ))

        ingress = k8s.V1beta1Ingress(api_version='extensions/v1beta1',
                                     kind='Ingress',
                                     metadata=k8s.V1ObjectMeta(
                                         name=k8s_name,
                                         labels={
                                             'name': k8s_name,
                                             'type': 'nauta-tensorboard',
                                             'nauta_app_name': 'tensorboard',
                                             'id': id
                                         },
                                         annotations={
                                             'nauta.ingress.kubernetes.io/rewrite-target': '/',
                                             'kubernetes.io/ingress.class': 'nauta-ingress'
                                         }
                                     ),
                                     spec=k8s.V1beta1IngressSpec(
                                         rules=[
                                             k8s.V1beta1IngressRule(
                                                 host='localhost',
                                                 http=k8s.V1beta1HTTPIngressRuleValue(
                                                     paths=[
                                                         k8s.V1beta1HTTPIngressPath(
                                                             path='/tb/' + id + "/",
                                                             backend=k8s.V1beta1IngressBackend(
                                                                 service_name=k8s_name,
                                                                 service_port=80
                                                             )
                                                         )
                                                     ]
                                                 )
                                             )
                                         ]
                                     ))

        return cls(deployment=deployment, service=service, ingress=ingress)
