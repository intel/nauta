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

from http import HTTPStatus
import os
import shutil
from typing import Dict, List, Optional

import yaml

from cli_text_consts import TemplateListCmdTexts as Texts
from util.config import Config
from util.github import Github, GithubException
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

    def __init__(self, name: str, description: str, local_version: str = None, remote_version: str = None):
        self.name = name
        self.description = description
        self.local_version = local_version
        self.remote_version = remote_version

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


def get_remote_templates(repository_name: str, access_token: str = None) -> Dict[str, Template]:
    remote_model_list = {}

    try:
        g = Github(repository_name=repository_name, token=access_token)
        contents = g.get_repository_content()
        for content in contents:
            file_path = "/".join([content.name, Template.CHART_FILE_LOCATION, Template.CHART_FILE_NAME])
            file = g.get_file_content(file_path=file_path)

            if file:
                remote_template = extract_chart_description(file, local=False)
                if remote_template:
                    remote_model_list[remote_template.name] = remote_template

        return remote_model_list
    except GithubException as gexe:
        logger.exception(Texts.OTHER_GITHUB_ERROR)
        message = Texts.OTHER_GITHUB_ERROR
        if gexe.status == HTTPStatus.NOT_FOUND:
            message = Texts.MISSING_REPOSITORY.format(repository_name=repository_name)
        elif gexe.status == HTTPStatus.UNAUTHORIZED:
            message = Texts.UNAUTHORIZED
        raise ExceptionWithMessage(message)
    except Exception as exe:
        logger.exception(Texts.OTHER_ERROR_DURING_ACCESSING_REMOTE_REPOSITORY)
        raise ExceptionWithMessage(Texts.OTHER_ERROR_DURING_ACCESSING_REMOTE_REPOSITORY) from exe


def extract_chart_description(chart_content: str, local: bool) -> Optional[Template]:
    chart = yaml.load(chart_content)

    name = chart.get(Template.CHART_NAME_FIELD)
    description = chart.get(Template.CHART_DESCRIPTION_FIELD)
    local_version = chart.get(Template.CHART_VERSION_FIELD) if local else None
    remote_version = chart.get(Template.CHART_VERSION_FIELD) if not local else None

    if name:
        return Template(name=name, description=description, local_version=local_version,
                        remote_version=remote_version)
    else:
        return None


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
    repository_name, access_token = get_repository_configuration()
    error_messages = []
    remote_template_list = {}
    try:
        remote_template_list = get_remote_templates(repository_name=repository_name, access_token=access_token)
    except ExceptionWithMessage as exe:
        error_messages.append(exe.message)

    local_template_list = {}
    try:
        local_template_list = get_local_templates()
    except Exception:
        logger.exception(Texts.ERROR_DURING_LOADING_LOCAL_TEMPLATES)
        error_messages.append(Texts.ERROR_DURING_LOADING_LOCAL_TEMPLATES)
    for key, value in remote_template_list.items():
        if key in local_template_list:
            value.local_version = local_template_list[key].local_version

    remote_template_list.update({key: value for (key, value) in local_template_list.items()
                                 if key not in remote_template_list})

    ret_list = []
    for key in sorted(remote_template_list.keys()):
        ret_list.append(remote_template_list[key].representation())

    return ret_list, error_messages


def get_repository_configuration() -> (Optional[str], Optional[str]):
    model_zoo_conf_file = os.path.join(Config().config_path, MODEL_ZOO_CONF_FILE)
    if not os.path.isfile(model_zoo_conf_file):
        return None, None

    with open(model_zoo_conf_file, "r") as file:
        content = file.read()
        configuration = yaml.load(content)

        model_zoo_address = configuration.get(MODEL_ZOO_ADDRESS_KEY)
        model_zoo_access_token = configuration.get(MODEL_ZOO_TOKEN_KEY)

        if model_zoo_address:
            return model_zoo_address, model_zoo_access_token

    return None, None
