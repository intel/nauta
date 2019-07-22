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

import os

import click
from collections import namedtuple
from enum import Enum
from sys import exit

from typing import List
import yaml

from cli_text_consts import ModelExportCommonTexts as Texts
from commands.common import save_logs_to_file, print_logs
from logs_aggregator.k8s_es_client import K8sElasticSearchClient
from platform_resources.workflow import ArgoWorkflow
from util.app_names import NAUTAAppNames
from util.config import Config
from util.exceptions import K8sProxyOpenError, K8sProxyCloseError, LocalPortOccupiedError
from util.k8s.k8s_info import get_kubectl_current_context_namespace
from util.k8s.k8s_proxy_context_manager import K8sProxy
from util.logger import initialize_logger
from util.system import handle_error


MODEL_HEADERS = ['Operation', 'Start date', 'End date', 'Owner', 'State']
STEP_HEADERS = ['Name', 'Start date', 'End date', 'State']

EXPORT_LIST_HEADERS = ['Name', 'Parameters description']
PROCESS_LIST_HEADERS = ['Name']

PROCESS_WORKFLOWS_LOCATION = 'workflows/processes'
EXPORT_WORKFLOWS_LOCATION = 'workflows/exports'

workflow_description = namedtuple('Description', ['name', 'parameters'])

logger = initialize_logger(__name__)


class PodPhase(Enum):
    Pending = 'Pending'
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'
    Unknown = 'Unknown'


def get_list_of_workflows(location: str) -> List[workflow_description]:
    path = os.path.join(Config().config_path, location)

    list_of_workflows = []
    for name in os.listdir(path):
        description = format_workflow_description(os.path.join(path, name))
        list_of_workflows.append(description)

    return list_of_workflows


def format_workflow_description(filename: str) -> workflow_description:
    with open(filename, mode='r', encoding='utf-8') as workflow_content_file:
        workflow_content = yaml.safe_load(workflow_content_file) or {}
        name = workflow_content.get('metadata', {}).get('generateName')
        description = workflow_content.get('metadata', {}).get('paramDescription')
        return workflow_description(name=name, parameters=description.replace("\\n", "\n") if description else "---")


def get_logs(operation_name: str, start_date: str, end_date: str, match: str, output: bool,
             pager: bool, follow: bool):
    """
    Show logs for a given model export operation.
    """
    # check whether we have operations with a given name
    if operation_name and match:
        handle_error(user_msg=Texts.NAME_M_BOTH_GIVEN_ERROR_MSG)
        exit(1)
    elif not operation_name and not match:
        handle_error(user_msg=Texts.NAME_M_NONE_GIVEN_ERROR_MSG)
        exit(1)

    try:
        with K8sProxy(NAUTAAppNames.ELASTICSEARCH) as proxy:
            es_client = K8sElasticSearchClient(host="127.0.0.1", port=proxy.tunnel_port,
                                               verify_certs=False, use_ssl=False)
            namespace = get_kubectl_current_context_namespace()
            if match:
                operation_name = match
                name_filter = match
            else:
                name_filter = f'^{operation_name}$'
            workflows = ArgoWorkflow.list(namespace=namespace, name_filter=name_filter)
            if not workflows:
                raise ValueError(f'Operation with given name: {operation_name} does not '
                                 f'exists in namespace {namespace}.')

            follow_logs = True if follow and not output else False

            if output and len(workflows) > 1:
                click.echo(Texts.MORE_EXP_LOGS_MESSAGE)

            for workflow in workflows:
                start_date = start_date if start_date else workflow.started_at

                ops_logs_generator = es_client.get_argo_workflow_logs_generator(workflow=workflow, namespace=namespace,
                                                                                start_date=start_date,
                                                                                end_date=end_date,
                                                                                follow=follow_logs)

                if output:
                    save_logs_to_file(logs_generator=ops_logs_generator,
                                      instance_name=workflow.name, instance_type="operation")
                else:
                    if len(workflows) > 1:
                        click.echo(f'Operation : {workflow.name}')
                    print_logs(run_logs_generator=ops_logs_generator, pager=pager)

    except K8sProxyCloseError:
        handle_error(logger, Texts.PROXY_CLOSE_LOG_ERROR_MSG, Texts.PROXY_CLOSE_LOG_ERROR_MSG)
        exit(1)
    except LocalPortOccupiedError as exe:
        handle_error(logger, Texts.LOCAL_PORT_OCCUPIED_ERROR_MSG.format(exception_message=exe.message),
                     Texts.LOCAL_PORT_OCCUPIED_ERROR_MSG.format(exception_message=exe.message))
        exit(1)
    except K8sProxyOpenError:
        handle_error(logger, Texts.PROXY_CREATION_ERROR_MSG, Texts.PROXY_CREATION_ERROR_MSG)
        exit(1)
    except ValueError:
        handle_error(logger, Texts.OPERATION_NOT_EXISTS_ERROR_MSG.format(operation_name=operation_name),
                     Texts.OPERATION_NOT_EXISTS_ERROR_MSG.format(experiment_name=operation_name))
        exit(1)
    except Exception:
        handle_error(logger, Texts.LOGS_GET_OTHER_ERROR_MSG,
                     Texts.LOGS_GET_OTHER_ERROR_MSG)
        exit(1)
