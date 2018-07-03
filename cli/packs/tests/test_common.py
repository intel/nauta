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

import unittest.mock as mock

import packs.common as common

PREP_LIST_OUTPUT = '''RUN mkdir .dlsctl/tmp/t20180416164710727 
COPY .dlsctl/tmp/t20180416164710727/* .dlsctl/tmp/t20180416164710727/ 
RUN mkdir .dlsctl/tmp/t20180416164710727/charts 
COPY .dlsctl/tmp/t20180416164710727/charts/* .dlsctl/tmp/t20180416164710727/charts/ 
RUN mkdir .dlsctl/tmp/t20180416164710727/charts/tf-training 
COPY .dlsctl/tmp/t20180416164710727/charts/tf-training/* .dlsctl/tmp/t20180416164710727/charts/tf-training/ 
RUN mkdir .dlsctl/tmp/t20180416164710727/charts/tf-training/templates 
COPY .dlsctl/tmp/t20180416164710727/charts/tf-training/templates/* .dlsctl/tmp/t20180416164710727/charts/tf-training/templates/ 
RUN mkdir .dlsctl/tmp/t20180416164710727/charts/tf-training/charts 
COPY .dlsctl/tmp/t20180416164710727/charts/tf-training/charts/* .dlsctl/tmp/t20180416164710727/charts/tf-training/charts/'''

PREP_LIST_INPUT = [('/.dlsctl/tmp/t20180416164609672/charts/tf-training/charts', [], []),
     ('/.dlsctl/tmp/t20180416164609672', ['charts'], ['app.py', '.draftignore', 'Dockerfile', 'draft.toml']),
     ('/.dlsctl/tmp/t20180416164609672/charts', ['tf-training'], []),
     ('/.dlsctl/tmp/t20180416164609672/charts/tf-training', ['templates', 'charts'],
      ['values.yaml', '.helmignore', 'Chart.yaml']),
     ('/.dlsctl/tmp/t20180416164609672/charts/tf-training/templates', [], ['job.yaml', '_helpers.tpl']),
     ('/.dlsctl/tmp/t20180416164609672/charts/tf-training/charts', [], []),
     ('/.dlsctl/tmp/t20180416164710727', ['charts'], ['app.py', '.draftignore', 'Dockerfile', 'draft.toml']),
     ('/.dlsctl/tmp/t20180416164710727/charts', ['tf-training'], []),
     ('/.dlsctl/tmp/t20180416164710727/charts/tf-training', ['templates', 'charts'],
      ['values.yaml', '.helmignore', 'Chart.yaml']),
     ('/.dlsctl/tmp/t20180416164710727/charts/tf-training/templates', [], ['job.yaml', '_helpers.tpl']),
     ('/.dlsctl/tmp/t20180416164710727/charts/tf-training/charts', [], [])]

PARAMETERS = ("--param1=value1", "-param2=value2", "param3=value3")
SCRIPT_LOCATION = "training_script.py"


def compare_list(param_list, str, script_name):
    if script_name:
        assert param_list[0] == script_name, "missing script name in list of arguments"

    local_list = list(str)
    index = 0

    for param in param_list:
        if script_name:
            continue

        assert param == local_list[index], "missing argument"
        index = index + 1


def test_prepare_script_parameters():
    output = common.prepare_script_paramaters(PARAMETERS, SCRIPT_LOCATION)

    assert len(output) == 4, "Not all PARAMETERS were processed - with script name."
    compare_list(output, PARAMETERS, SCRIPT_LOCATION)

    output = common.prepare_script_paramaters(PARAMETERS, SCRIPT_LOCATION, False)

    assert len(output) == 3, "Not all PARAMETERS were processed - without script name."
    compare_list(output, PARAMETERS, "")