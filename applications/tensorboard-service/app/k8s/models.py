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

from hashlib import sha1
import os
from typing import Dict, List

from kubernetes import client as k8s


class K8STensorboardInstance:
    EXPERIMENTS_OUTPUT_VOLUME_NAME = 'output-home'
    TENSORBOARD_CONTAINER_MOUNT_PATH_PREFIX = '/mnt/exp'

    def __init__(self, deployment: k8s.V1Deployment, service: k8s.V1Service, ingress: k8s.V1beta1Ingress,
                 pod: k8s.V1Pod = None):
        self.deployment = deployment
        self.service = service
        self.ingress = ingress
        self.pod = pod

    @staticmethod
    def generate_run_names_hash(run_names: List[str]) -> str:
        run_names.sort()
        run_names_str = ",".join(run_names)
        run_names_hash = sha1(run_names_str.encode('utf-8')).hexdigest()
        return run_names_hash

    @classmethod
    def from_run_name(cls, id: str, run_names_list: List[str]):
        k8s_name = 'tensorboard-' + id
        run_names_hash = K8STensorboardInstance.generate_run_names_hash(run_names_list)

        volume_mounts = []

        for run_name in run_names_list:
            mount = k8s.V1VolumeMount(
                name=cls.EXPERIMENTS_OUTPUT_VOLUME_NAME,
                mount_path=os.path.join(cls.TENSORBOARD_CONTAINER_MOUNT_PATH_PREFIX, run_name),
                sub_path=run_name
            )
            volume_mounts.append(mount)

        deployment_labels = {
            'name': k8s_name,
            'type': 'dls4e-tensorboard',
            'dls4e_app_name': 'tensorboard',
            'id': id,
            'run-names-hash': run_names_hash
        }

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
                                                  containers=[
                                                      k8s.V1Container(
                                                          name='app',
                                                          image='tensorflow/tensorflow:1.8.0-py3',
                                                          command=["tensorboard",
                                                                   "--logdir", "/mnt/exp",
                                                                   "--port", "80",
                                                                   "--host", "0.0.0.0"
                                                                   ],
                                                          volume_mounts=volume_mounts,
                                                          ports=[
                                                              k8s.V1ContainerPort(
                                                                  container_port=80
                                                              )
                                                          ]
                                                      )
                                                  ],
                                                  volumes=[
                                                      k8s.V1Volume(
                                                          name='output-home',
                                                          persistent_volume_claim=  # noqa
                                                          k8s.V1PersistentVolumeClaimVolumeSource(
                                                              claim_name='output-home',
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
                                        'type': 'dls4e-tensorboard',
                                        'dls4e_app_name': 'tensorboard',
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
                                        'type': 'dls4e-tensorboard',
                                        'dls4e_app_name': 'tensorboard',
                                        'id': id
                                    }
                                ))

        ingress = k8s.V1beta1Ingress(api_version='extensions/v1beta1',
                                     kind='Ingress',
                                     metadata=k8s.V1ObjectMeta(
                                         name=k8s_name,
                                         labels={
                                             'name': k8s_name,
                                             'type': 'dls4e-tensorboard',
                                             'dls4e_app_name': 'tensorboard',
                                             'id': id
                                         },
                                         annotations={
                                             'dls.ingress.kubernetes.io/rewrite-target': '/',
                                             'kubernetes.io/ingress.class': 'dls-ingress'
                                         }
                                     ),
                                     spec=k8s.V1beta1IngressSpec(
                                         rules=[
                                             k8s.V1beta1IngressRule(
                                                 host='localhost',
                                                 http=k8s.V1beta1HTTPIngressRuleValue(
                                                     paths=[
                                                         k8s.V1beta1HTTPIngressPath(
                                                             path='/tb/' + id,
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
