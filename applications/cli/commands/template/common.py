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
import shutil
from http import HTTPStatus
from typing import Dict, List, Optional

import requests
import yaml

from cli_text_consts import TemplateListCmdTexts as Texts
from util.config import Config
from util.logger import initialize_logger
from util.exceptions import ExceptionWithMessage
import commands.experiment.common


MODEL_ZOO_ADDRESS_KEY = "model-zoo-address"
MODEL_ZOO_TOKEN_KEY = "access-token"
MODEL_ZOO_CONF_FILE = "zoo-repository.config"

TEMPLATE_NAME = "Template name"
TEMPLATE_DESCRIPTION = "Template description"
TEMPLATE_LOCAL_VERSION = "Local version"
TEMPLATE_REMOTE_VERSION = "Remote version"

TEMPLATE_LIST_HEADERS = [TEMPLATE_NAME, TEMPLATE_DESCRIPTION, TEMPLATE_LOCAL_VERSION, TEMPLATE_REMOTE_VERSION]

logger = initialize_logger(__name__)


class Template:
    CHART_FILE_LOCATION = "charts"
    CHART_FILE_NAME = "Chart.yaml"

    CHART_NAME_FIELD = "name"
    CHART_VERSION_FIELD = "version"
    CHART_DESCRIPTION_FIELD = "description"

    DESCRIPTION_MAX_WIDTH = 50

    def __init__(self, name: str, description: str, local_version: str = None, remote_version: str = None,
                 url: str = None):
        self.name = name
        self.description = description
        self.local_version = local_version
        self.remote_version = remote_version
        self.url = url  # Url of remote template's package

    def representation(self):
        return str(self.name), commands.experiment.common.wrap_text(str(self.description),
                                                                    width=Template.DESCRIPTION_MAX_WIDTH, spaces=0),\
               str(self.local_version), str(self.remote_version)

    def update_chart_yaml(self, chart_yaml_path: str):
        with open(chart_yaml_path, mode='r', encoding='utf-8') as chart_yaml_file:
            chart_definition = yaml.safe_load(chart_yaml_file)

        chart_definition['name'] = self.name
        chart_definition['description'] = self.description
        chart_definition['version'] = self.local_version

        with open(chart_yaml_path, mode='w', encoding='utf-8') as chart_yaml_file:
            yaml.safe_dump(chart_definition, chart_yaml_file, default_flow_style=False)

    def render_from_existing_template(self, src_template_name: str):
        local_templates_dir = os.path.join(Config.get_config_path(), "packs")
        src_template_dir = os.path.join(local_templates_dir, src_template_name)
        dest_template_dir = os.path.join(local_templates_dir, self.name)
        try:
            shutil.copytree(src_template_dir, dest_template_dir)
            chart_yaml_path = os.path.join(dest_template_dir, Template.CHART_FILE_LOCATION, Template.CHART_FILE_NAME)
            self.update_chart_yaml(chart_yaml_path)
        except (IOError, KeyError, shutil.Error):
            shutil.rmtree(dest_template_dir)  # Clear destination directory in case of template copy error
            raise


def get_remote_templates(repository_address: str) -> Dict[str, Template]:
    try:
        remote_manifest = requests.get(f'{repository_address}/index.json')
        remote_manifest.raise_for_status()
        templates_metadata = remote_manifest.json()['templates']
    except requests.exceptions.HTTPError as exe:
        if exe.response.status_code == HTTPStatus.NOT_FOUND:
            logger.exception(ExceptionWithMessage(Texts.MISSING_REPOSITORY.format(
                repository_address=repository_address)))
            raise ExceptionWithMessage(Texts.MISSING_REPOSITORY.format(repository_address=repository_address)) from exe
        else:
            logger.exception(ExceptionWithMessage(Texts.OTHER_ERROR_DURING_ACCESSING_REMOTE_REPOSITORY))
            raise ExceptionWithMessage(Texts.OTHER_ERROR_DURING_ACCESSING_REMOTE_REPOSITORY) from exe
    except Exception as exe:
        logger.exception(ExceptionWithMessage(Texts.OTHER_ERROR_DURING_ACCESSING_REMOTE_REPOSITORY))
        raise ExceptionWithMessage(Texts.OTHER_ERROR_DURING_ACCESSING_REMOTE_REPOSITORY) from exe

    remote_templates = {template['name']: Template(name=template['name'],
                                                   remote_version=template['version'],
                                                   description=template['description'],
                                                   url=template['url'],
                                                   local_version=None) for template in templates_metadata}

    return remote_templates


def extract_chart_description(chart_content: str, local: bool) -> Optional[Template]:
    chart = yaml.safe_load(chart_content)

    name = chart.get(Template.CHART_NAME_FIELD)
    description = chart.get(Template.CHART_DESCRIPTION_FIELD)
    local_version = chart.get(Template.CHART_VERSION_FIELD) if local else None
    remote_version = chart.get(Template.CHART_VERSION_FIELD) if not local else None

    if name:
        return Template(name=name, description=description, local_version=local_version,
                        remote_version=remote_version)
    else:
        return None


def load_remote_template(name: str, repository_address: str) -> Optional[Template]:
    remote_templates = get_remote_templates(repository_address)

    if not remote_templates.get(name):
        logger.debug(f'Template {name} not found in repository {repository_address}')
        return None

    return remote_templates[name]


def download_remote_template(template: Template, repository_address: str, output_dir_path: str):
    pack_filename = f'{output_dir_path}/{template.name}-{template.remote_version}.tar.bz2'

    template_pack_tar = requests.get(f'{repository_address}/{template.url}', stream=True)
    with open(pack_filename, 'wb') as f:
        f.write(template_pack_tar.raw.read())

    shutil.unpack_archive(pack_filename, output_dir_path)


def get_template_version(template_name: str) -> Optional[str]:
    chart_file_location = os.path.join(Config.get_config_path(), "packs", template_name,
                                       Template.CHART_FILE_LOCATION, Template.CHART_FILE_NAME)

    if os.path.isfile(chart_file_location):
        with open(chart_file_location, "r") as file:
            local_template = extract_chart_description(file.read(), local=True)
            return local_template.local_version

    return None


def get_local_templates() -> Dict[str, Template]:
    local_model_list = {}
    path = os.path.join(Config.get_config_path(), "packs")

    for (dirpath, dirnames, filenames) in os.walk(path):
        template_name = os.path.split(os.path.split(dirpath)[0])[1]
        chart_file_location = os.path.join(path, template_name, Template.CHART_FILE_LOCATION, Template.CHART_FILE_NAME)
        if os.path.isfile(chart_file_location):
            with open(chart_file_location, "r") as file:
                local_template = extract_chart_description(file.read(), local=True)
                if local_template:
                    local_model_list[local_template.name] = local_template

    return local_model_list


def prepare_list_of_templates() -> (List[Template], List[str]):
    error_messages = []
    remote_templates = {}
    try:
        repository_address = get_repository_address()
        remote_templates = get_remote_templates(repository_address)
    except ExceptionWithMessage as exe:
        error_messages.append(exe.message)

    local_templates = {}
    try:
        local_templates = get_local_templates()
    except Exception:
        logger.exception(Texts.ERROR_DURING_LOADING_LOCAL_TEMPLATES)
        error_messages.append(Texts.ERROR_DURING_LOADING_LOCAL_TEMPLATES)
    for key, remote_template in remote_templates.items():
        if key in local_templates:
            remote_template.local_version = local_templates[key].local_version

    remote_templates.update({key: local_template for (key, local_template) in local_templates.items()
                            if key not in remote_templates})

    ret_list = []
    for key in sorted(remote_templates.keys()):
        ret_list.append(remote_templates[key].representation())

    return ret_list, error_messages


def get_repository_address() -> Optional[str]:
    model_zoo_conf_file = os.path.join(Config().config_path, MODEL_ZOO_CONF_FILE)
    if not os.path.isfile(model_zoo_conf_file):
        return None

    with open(model_zoo_conf_file, "r") as file:
        content = file.read()
        configuration = yaml.safe_load(content)
        model_zoo_address = configuration.get(MODEL_ZOO_ADDRESS_KEY)
        if model_zoo_address:
            return model_zoo_address

    return None
