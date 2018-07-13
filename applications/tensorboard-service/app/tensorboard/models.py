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

from enum import Enum
from typing import Dict


class TensorboardStatus(Enum):
    CREATING = 'CREATING'
    RUNNING = 'RUNNING'


class Tensorboard:
    def __init__(self, id: str, status: TensorboardStatus = TensorboardStatus.CREATING, url: str = ''):
        self.id = id
        self.status = status
        self.url = url

    def to_dict(self) -> Dict[str, str]:
        return {
            'id': self.id,
            'status': self.status.value,
            'url': self.url
        }


class Run:
    def __init__(self, name: str, owner: str):
        self.name = name
        self.owner = owner
