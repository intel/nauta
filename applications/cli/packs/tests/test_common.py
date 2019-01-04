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

    assert len(output) == 4, "Not all PARAMETERS were processed."
    compare_list(output, PARAMETERS, SCRIPT_LOCATION)
