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


from typing import List

from k8s.models import K8STensorboardInstance
from kubernetes import client as kube_models


def test_generate_tensorboard_deployment():
    fake_run_names_list = ["some-run-3", "some-run-2", "some-run-1"]
    model_instance = K8STensorboardInstance.from_run_name(id='a7db5449-6168-4010-9ce6-cbaefbbfa4a1',
                                                          run_names_list=fake_run_names_list)

    assert model_instance.deployment.metadata.name == "tensorboard-a7db5449-6168-4010-9ce6-cbaefbbfa4a1"

    volume_mounts: List[kube_models.V1VolumeMount] = model_instance.deployment.spec.template.spec.containers[0].volume_mounts

    assert len(volume_mounts) == len(fake_run_names_list)

    for mount in volume_mounts:
        mount.mount_path == '/mnt/exp/'