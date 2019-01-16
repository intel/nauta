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

import random
from typing import List

from k8s.models import K8STensorboardInstance
from kubernetes import client as kube_models
from tensorboard.models import Run


def test_generate_tensorboard_deployment(mocker):
    mocker.patch('k8s.models.NautaPlatformConfig')
    fake_runs = [
        Run(
            name="some-run-3",
            owner='alice'
        ),
        Run(
            name="some-run-2",
            owner='alice'
        ),
        Run(
            name="some-run-1",
            owner='bob'
        ),
    ]

    model_instance = K8STensorboardInstance.from_runs(id='a7db5449-6168-4010-9ce6-cbaefbbfa4a1', runs=fake_runs)

    assert model_instance.deployment.metadata.name == "tensorboard-a7db5449-6168-4010-9ce6-cbaefbbfa4a1"

    volume_mounts: List[kube_models.V1VolumeMount] = \
        model_instance.deployment.spec.template.spec.containers[0].volume_mounts

    assert len(volume_mounts) == len(fake_runs)


def test_generate_run_names_hash():
    fake_runs = [
        Run(
            name="some-run-3",
            owner='alice'
        ),
        Run(
            name="some-run-2",
            owner='alice'
        ),
        Run(
            name="some-run-1",
            owner='bob'
        ),
    ]

    expected_hash = '72c9324ef4a28d65dc5d134bb0edc77fb700bd79'

    run_names_hash_original = K8STensorboardInstance.generate_run_names_hash(fake_runs)

    random.shuffle(fake_runs)

    run_names_hash_suffled = K8STensorboardInstance.generate_run_names_hash(fake_runs)

    assert run_names_hash_original == expected_hash
    assert run_names_hash_suffled == expected_hash
