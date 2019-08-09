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
import sys

import click
import yaml


from util.cli_state import common_options, pass_state, State
from cli_text_consts import ConfigCmdTexts as Texts
from util.aliascmd import AliasCmd
from util.config import Config, NAUTAConfigMap
from util.logger import initialize_logger
from util.spinner import spinner
from util.system import handle_error
from util.template import override_values_in_packs, validate_cpu_settings, validate_memory_settings, \
    convert_k8s_memory_resource, convert_k8s_cpu_resource


NODE_CONFIG_FILENAME = "node_config"

CPU_NUMBER_FIELDNAME = "cpu_number"
MEMORY_AMOUNT_FIELDNAME = "memory_amount"
CPU_SYSTEM_REQUIRED_MIN_FIELDNAME = "cpu_system_required_min"
CPU_SYSTEM_REQUIRED_PERCENT_FIELDNAME = "cpu_system_required_percent"
MEMORY_SYSTEM_REQUIRED_MIN_FIELDNAME = "memory_system_required_min"
MEMORY_SYSTEM_REQUIRED_PERCENT_FIELDNAME = "memory_system_required_percent"

logger = initialize_logger(__name__)


def update_resources_in_packs(cpu: str = None, memory: str = None):
    config_file_location = os.path.join(Config().config_path, NODE_CONFIG_FILENAME)

    if not os.path.isfile(config_file_location):
        handle_error(logger, Texts.MISSING_CONFIG_FILE, Texts.MISSING_CONFIG_FILE)
        sys.exit(1)

    with open(config_file_location, 'r+', encoding='utf-8') as config_file, \
            spinner(text=Texts.CONFIG_UPDATE):
        config_file_content = yaml.safe_load(config_file)
        cpu_number = str(config_file_content.get(CPU_NUMBER_FIELDNAME))
        memory_amount = str(config_file_content.get(MEMORY_AMOUNT_FIELDNAME))
        cpu_system_required_min = str(config_file_content.get(CPU_SYSTEM_REQUIRED_MIN_FIELDNAME))
        cpu_system_required_percent = str(config_file_content.get(CPU_SYSTEM_REQUIRED_PERCENT_FIELDNAME))
        memory_system_required_min = str(config_file_content.get(MEMORY_SYSTEM_REQUIRED_MIN_FIELDNAME))
        memory_system_required_percent = str(config_file_content.get(MEMORY_SYSTEM_REQUIRED_PERCENT_FIELDNAME))

        if not cpu_number or cpu_number == "None" or not memory_amount or memory_amount == "None":
            handle_error(logger, Texts.CONFIG_FILE_INCORRECT, Texts.CONFIG_FILE_INCORRECT)
            sys.exit(1)

        new_cpu = cpu if cpu else cpu_number
        new_memory = memory if memory else memory_amount

        try:
            override_values_in_packs(new_cpu_number=new_cpu, new_memory_amount=new_memory,
                                     current_cpu_number=cpu_number,
                                     current_mem_amount=memory_amount, cpu_system_required_min=cpu_system_required_min,
                                     cpu_system_required_percent=cpu_system_required_percent,
                                     mem_system_required_min=memory_system_required_min,
                                     mem_system_required_percent=memory_system_required_percent)
        except Exception:
            logger.exception(Texts.ERROR_DURING_UPDATE)
            handle_error(logger, Texts.ERROR_DURING_UPDATE, Texts.ERROR_DURING_UPDATE)
            sys.exit(1)

        if new_cpu != cpu_number and new_memory != memory_amount:
            config_file.seek(0)
            config_file.truncate()
            config_file_content[CPU_NUMBER_FIELDNAME] = cpu
            config_file_content[MEMORY_AMOUNT_FIELDNAME] = memory
            yaml.safe_dump(config_file_content, config_file, default_flow_style=False, explicit_start=True)


@click.command(help=Texts.HELP, short_help=Texts.HELP, cls=AliasCmd, alias='cfg', options_metavar='[options]')
@click.option("-c", "--cpu", default=None, help=Texts.HELP_C)
@click.option("-m", "--memory", default=None, help=Texts.HELP_M)
@common_options(verify_dependencies=False)
@pass_state
def config(state: State, cpu: str, memory: str):

    if not cpu or not memory:
        handle_error(logger, Texts.MISSING_ARGUMENTS, Texts.MISSING_ARGUMENTS)
        sys.exit(1)

    if not validate_cpu_settings(cpu):
        handle_error(logger, Texts.CPU_WRONG_FORMAT, Texts.CPU_WRONG_FORMAT)
        sys.exit(1)

    if not validate_memory_settings(memory):
        handle_error(logger, Texts.MEMORY_WRONG_FORMAT, Texts.MEMORY_WRONG_FORMAT)
        sys.exit(1)

    configuration = NAUTAConfigMap()

    if configuration.minimal_node_memory_amount and \
       convert_k8s_memory_resource(configuration.minimal_node_memory_amount) > convert_k8s_memory_resource(memory):
        error_message = Texts.MEMORY_SETTINGS_TOO_LOW.format(memory_value=configuration.minimal_node_memory_amount)
        handle_error(logger, error_message, error_message)
        sys.exit(1)

    if configuration.minimal_node_cpu_number and \
       convert_k8s_cpu_resource(configuration.minimal_node_cpu_number) > convert_k8s_cpu_resource(cpu):
        error_message = Texts.CPU_SETTINGS_TOO_LOW.format(cpu_value=configuration.minimal_node_cpu_number)
        handle_error(logger, error_message, error_message)
        sys.exit(1)

    update_resources_in_packs(cpu, memory)

    click.echo(Texts.SUCCESS_MESSAGE)
