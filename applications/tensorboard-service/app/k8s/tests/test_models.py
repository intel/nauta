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

import random
from typing import List

from k8s.models import K8STensorboardInstance
from kubernetes import client as kube_models
from tensorboard.models import Run


def test_generate_tensorboard_deployment(mocker):
    mocker.patch('k8s.models.Dls4ePlatformConfig')
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
