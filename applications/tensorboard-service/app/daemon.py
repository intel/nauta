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

import logging as log
from time import sleep

from tensorboard.tensorboard import TensorboardManager


log.basicConfig(level=log.DEBUG)

log.debug('daemon started!')

mgr = TensorboardManager.incluster_init()

while True:
    mgr.delete_garbage()
    log.debug('sleeping for 5 seconds...')
    sleep(5)
