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

import json
import logging as log

from flask import Flask

from tensorboard import TensorboardManager

log.basicConfig(level=log.DEBUG)

app = Flask(__name__)


@app.route('/create/<run_name>', methods=['POST'])
def create(run_name: str):

    tensb_mgr = TensorboardManager.incluster_init()

    current_tensorboard_instance = tensb_mgr.get(run_name)

    if current_tensorboard_instance:
        response = {
            "url": "/tb/" + run_name + "/"
        }
        return json.dumps(response), 409

    url = tensb_mgr.create(run_name)

    response = {
        "url": url + "/"
    }

    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
