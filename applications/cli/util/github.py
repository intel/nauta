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
import json
import os
from typing import List

import requests

from util.logger import initialize_logger
from cli_text_consts import GithubMessages as Texts

logger = initialize_logger(__name__)


class GithubException(Exception):
    def __init__(self, status: str = None):
        super().__init__()
        self.status = status


class GithubRepository:
    def __init__(self, name: str):
        self.name = name


class Github:

    GITHUB_URL = 'github.com'
    GITHUB_API_URL = 'https://api.github.com'
    GITHUB_DOWNLOAD_URL = "raw.githubusercontent.com"

    def __init__(self, repository_name, token):
        self.token = token
        self.repository_name = repository_name

    def make_get_request(self, url) -> str:
        headers = None
        if self.token:
            headers = {'Authorization': f'token {self.token}'}
        try:
            output = requests.get(url, headers=headers)

        except Exception as exe:
            logger.exception(Texts.GET_OTHER_ERROR)
            raise GithubException(HTTPStatus.SEE_OTHER) from exe

        if output.status_code == HTTPStatus.NOT_FOUND:
            logger.debug(Texts.GET_MISSING_FILE.format(url=url))
        elif output.status_code != HTTPStatus.OK:
            logger.error(Texts.GET_REQUEST_ERROR.format(url=url, http_code=output.status_code))
            raise GithubException(output.status_code)

        return output.text

    def get_repository_content(self) -> List[GithubRepository]:
        ret_list = []
        request_url = "/".join([self.GITHUB_API_URL, 'repos', self.repository_name, 'contents'])

        output = self.make_get_request(request_url)

        repo_item_list = json.loads(output)

        for item in repo_item_list:
            repository = GithubRepository(name=item.get("name"))
            ret_list.append(repository)

        return ret_list

    def get_file_content(self, file_path: str) -> str or None:
        request_url = "/".join([self.GITHUB_API_URL, "repos", self.repository_name, "contents", file_path])
        try:
            file_location = self.make_get_request(request_url)
            download_url = json.loads(file_location).get("download_url")

            if download_url:
                file = requests.get(download_url)
                return file.text if file else None
            return None
        except Exception:
            logger.exception(Texts.MISSING_CHART_FILE)

        return None

    def download_whole_directory(self, dirpath: str, output_dir_path: str):
        os.makedirs(output_dir_path)

        request_url = "/".join([self.GITHUB_API_URL, 'repos', self.repository_name, 'contents', dirpath])

        output = self.make_get_request(request_url)

        repo_item_list = json.loads(output)

        for item in repo_item_list:
            if item['type'] == 'file':
                file_content = self.get_file_content("/".join([dirpath, item['name']]))
                with open(os.path.join(output_dir_path, item['name']), mode='w') as file:
                    file.write(file_content)
            elif item['type'] == 'dir':
                self.download_whole_directory(dirpath="/".join([dirpath, item['name']]),
                                              output_dir_path=os.path.join(output_dir_path, item['name']))
