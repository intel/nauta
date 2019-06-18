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

import pytest
from unittest.mock import MagicMock, mock_open, patch
from typing import List

from platform_resources.workflow import ArgoWorkflow

workflow_w_two_param = ArgoWorkflow()
workflow_w_two_param.body = {'spec': {'arguments': {'parameters': [{'name': 'test-param-1', 'value': 'test-value-1'},
                                                                   {'name': 'test-param-2', 'value': 'test-value-2'}]}}}

workflow_wo_value = ArgoWorkflow()
workflow_wo_value.body = {'spec': {'arguments': {'parameters': [{'name': 'test-param-1', 'value': 'test-value-1'},
                                                                {'name': 'test-param-2'}]}}}

process_template = '''
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: process-template-
spec:
  entrypoint: process-template
  templates:
    {}
    - name: process-template
      container:
        image: "process-image"
        command: [process-command]
        args: ["-test-param"]
  tolerations:
    - key: "master"
      operator: "Exists"
      effect: "NoSchedule"
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: master
                operator: In
                values:
                  - "True"
'''

workflow_template = '''
---

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: workflow-template
spec:
  entrypoint: {}
  arguments:
    parameters:
      - name: cluster-registry-address
      - name: saved-model-dir-path
      - name: additional-params
        value: ''
  volumes:
    - name: input-home
      persistentVolumeClaim:
        claimName: input-home
    - name: input-public
      persistentVolumeClaim:
        claimName: input-public
    - name: output-home
      persistentVolumeClaim:
        claimName: output-home
    - name: output-public
      persistentVolumeClaim:
        claimName: output-public
  templates:
    {}
    - name: workflow-template
      inputs:
        parameters:
          - name: cluster-registry-address
          - name: saved-model-dir-path
          - name: additional-params
      container:
        image: "{{inputs.parameters.cluster-registry-address}}/nauta/openvino-mo:1.0.0"
        command: [bash]
        args: ["-c", "python3 mo.py --saved_model_dir {{inputs.parameters.saved-model-dir-path}} --output_dir /mnt/output/home/{{workflow.name}} {{inputs.parameters.additional-params}}"]
        volumeMounts:
          - name: input-home
            mountPath: /mnt/input/home
            readOnly: True
          - name: input-public
            mountPath: /mnt/input/root
            readOnly: True
          - name: output-home
            mountPath: /mnt/output/home
          - name: output-public
            mountPath: /mnt/output/root
            readOnly: True
          - name: output-public
            mountPath: /mnt/output/root/public
            subPath: public
          - name: input-public
            mountPath: /mnt/input/root/public
            subPath: public
  tolerations:
    - key: "master"
      operator: "Exists"
      effect: "NoSchedule"
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: master
                operator: In
                values:
                  - "True"
'''

workflow_steps = '''- name: step-template
      inputs:
        parameters:
          - name: cluster-registry-address
          - name: saved-model-dir-path
          - name: additional-params
      steps:
        - - name: step1
            template: step1-template
            arguments:
              parameters:
                - name: cluster-registry-address
                - name: saved-model-dir-path
                - name: additional-params
'''


def test_parameters():
    assert workflow_w_two_param.parameters == {'test-param-1': 'test-value-1', 'test-param-2': 'test-value-2'}


def test_set_parameters():
    workflow_w_two_param.parameters = {'test-param-2': 'new-value'}

    assert workflow_w_two_param.parameters == {'test-param-1': 'test-value-1', 'test-param-2': 'new-value'}


def test_set_parameters_error():
    with pytest.raises(KeyError):
        workflow_wo_value.parameters = {'test-param-1': 'new-value'}


def test_wait_for_completion(mocker):
    workflow_status_mock = MagicMock()
    workflow_status_mock.phase = 'Succeeded'
    get_workflow_mock = mocker.patch('platform_resources.workflow.ArgoWorkflow.get', return_value=workflow_status_mock)

    test_workflow = ArgoWorkflow()
    test_workflow.wait_for_completion()

    assert get_workflow_mock.call_count == 1


def test_wait_for_completion_failure(mocker):
    workflow_status_mock = MagicMock()
    workflow_status_mock.phase = 'Failed'
    get_workflow_mock = mocker.patch('platform_resources.workflow.ArgoWorkflow.get', return_value=workflow_status_mock)

    test_workflow = ArgoWorkflow()
    with pytest.raises(RuntimeError):
        test_workflow.wait_for_completion()

    assert get_workflow_mock.call_count == 1


def check_parameters(parameters: List[dict]):
    cra = None
    smd = None
    adp = None
    for parameter in parameters:
        name = parameter['name']
        if name == 'cluster-registry-address':
            cra = True
        elif name == 'saved-model-dir-path':
            smd = True
        elif name == 'additional-params':
            adp = True

    assert cra
    assert smd
    assert adp


def test_add_proces_add_steps(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    with patch('builtins.open', mock_open(read_data=workflow_template.format('workflow-template', ''))):
        main_workflow = ArgoWorkflow.from_yaml('workflow_template')
    with patch('builtins.open', mock_open(read_data=process_template.format(''))):
        process_workflow = ArgoWorkflow.from_yaml('process_template')

    main_workflow.add_process(process_workflow)

    spec = main_workflow.body['spec']
    assert spec['entrypoint'] == 'workflow-template-process-template'

    list_of_templates = spec['templates']

    process_template_exists = False
    flow_template_exists = False

    for template in list_of_templates:
        if template['name'] == 'workflow-template-process-template':
            flow_template_exists = True
            assert template.get('steps')
            assert len(template.get('steps')) == 2

            swt = None
            pwt = None

            for step in template.get('steps'):
                step_name = step[0]['name']
                if step_name == 'workflow-template':
                    swt = step
                elif step_name == 'process-template':
                    pwt = step

            parameters = step[0].get('arguments', []).get('parameters', [])
            assert parameters
            check_parameters(parameters)

            assert swt
            assert pwt

        elif template['name'] == 'process-template':
            process_template_exists = True
            parameters = template.get('inputs', []).get('parameters')
            assert parameters
            check_parameters(parameters)

    assert process_template_exists
    assert flow_template_exists


def test_add_process_with_steps(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    with patch('builtins.open', mock_open(read_data=workflow_template.format('step-template', workflow_steps))):
        main_workflow = ArgoWorkflow.from_yaml('workflow_template')
    with patch('builtins.open', mock_open(read_data=process_template.format(''))):
        process_workflow = ArgoWorkflow.from_yaml('process_template')

    main_workflow.add_process(process_workflow)

    spec = main_workflow.body['spec']
    assert spec['entrypoint'] == 'step-template'

    list_of_templates = spec['templates']

    process_template_exists = False
    flow_template_exists = False
    step_template_exists = False

    for template in list_of_templates:
        if template['name'] == 'step-template':
            step_template_exists = True
            assert template.get('steps')
            assert len(template.get('steps')) == 2

            swt = None
            pwt = None

            for step in template.get('steps'):
                step_name = step[0]['name']
                if step_name == 'step1':
                    swt = step
                elif step_name == 'process-template':
                    pwt = step

            parameters = step[0].get('arguments', []).get('parameters', [])
            assert parameters
            check_parameters(parameters)

            assert swt
            assert pwt

        elif template['name'] == 'workflow-template':
            flow_template_exists = True

        elif template['name'] == 'process-template':
            process_template_exists = True
            parameters = template.get('inputs', []).get('parameters')
            assert parameters
            check_parameters(parameters)

    assert process_template_exists
    assert flow_template_exists
    assert step_template_exists


def test_add_process_with_steps_in_process(mocker):
    mocker.patch('kubernetes.config.load_kube_config')
    with patch('builtins.open', mock_open(read_data=workflow_template.format('workflow-template', ''))):
        main_workflow = ArgoWorkflow.from_yaml('workflow_template')
    with patch('builtins.open', mock_open(read_data=process_template.format(workflow_steps))):
        process_workflow = ArgoWorkflow.from_yaml('process_template')

    main_workflow.add_process(process_workflow)

    spec = main_workflow.body['spec']
    list_of_templates = spec['templates']

    flow_template_exists = False

    for template in list_of_templates:
        if template['name'] == 'workflow-template-process-template':
            flow_template_exists = True
            assert template.get('steps')
            assert len(template.get('steps')) == 2

            swt = None
            pwt = None

            for step in template.get('steps'):
                step_name = step[0]['name']
                if step_name == 'step-template':
                    swt = step
                elif step_name == 'workflow-template':
                    pwt = step

            parameters = step[0].get('arguments', []).get('parameters', [])
            assert parameters
            check_parameters(parameters)

            assert swt
            assert pwt

    assert flow_template_exists
