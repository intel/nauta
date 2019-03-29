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
from typing import Tuple

from cli_text_consts import DraftCmdTexts as Texts
from util import helm
from util.config import Config
from util.filesystem import copytree_content
from util.logger import initialize_logger

logger = initialize_logger(__name__)


class NoPackError(Exception):
    pass


def create(working_directory: str = None, pack_type: str = None) -> Tuple[str, int]:
    try:
        config_dirpath = Config().get_config_path()

        packs_dirpath = os.path.join(config_dirpath, 'packs')

        requested_pack_path = os.path.join(packs_dirpath, pack_type)

        if not os.path.isdir(requested_pack_path):
            raise NoPackError(f'no pack found with name: {requested_pack_path}')

        helm_chart_destination_dirpath = f"{working_directory}/charts/{pack_type}"
        os.makedirs(helm_chart_destination_dirpath)

        copytree_content(f"{requested_pack_path}", f"{working_directory}", ignored_objects=['charts'])
        copytree_content(f"{requested_pack_path}/charts", helm_chart_destination_dirpath)
    except NoPackError as ex:
        # TODO: these exceptions should be reraised instead caught here
        logger.exception(ex)
        return Texts.PACK_NOT_EXISTS, 1
    except Exception as ex:
        logger.exception(ex)
        return Texts.DEPLOYMENT_NOT_CREATED, 100

    return "", 0


def up(run_name: str, working_directory: str = None, namespace: str = None):
    try:
        dirs = os.listdir(f"{working_directory}/charts")
        helm.install_helm_chart(f"{working_directory}/charts/{dirs[0]}",
                                release_name=run_name,
                                tiller_namespace=namespace)
    except Exception as ex:
        logger.exception(ex)
        raise
