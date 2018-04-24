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

import re
from typing import List

from draft.cmd import call_draft
from util.system import execute_system_command
from util.logger import initialize_logger

log = initialize_logger('draft.dependencies_checker')

DRAFT_SUPPORTED_VERSIONS = ['78385afe65500ebb4f546341f229a5f200f1128a']
KUBECTL_SUPPORTED_VERSIONS = ['fc32d2f3698e36b93322a3465f63a14e9f0eaead']
HELM_SUPPORTED_VERSIONS = ['a80231648a1473929271764b920a8e346f6de844']
DOCKER_SUPPORTED_VERSIONS = ['18.03.0-ce']


def _check_go_app_version(app_name: str, version_output: str, expected_versions: List[str]):
    regex = r"GitCommit:\"([0-9a-f]+)\""

    matches = re.findall(regex, version_output)

    if len(matches) != 1:
        raise RuntimeError('parsing {app_name} version failed!'.format(app_name=app_name))

    supported_versions = expected_versions
    installed_version = matches[0]

    if installed_version in supported_versions:
        log.info('{app_name} verified successfully'.format(app_name=app_name))
    else:
        log.warning('{app_name} installed version ({installed}) was not tested, supported versions: {supported}'
                    .format(installed=installed_version, supported=supported_versions, app_name=app_name))


def check():
    # draft
    output, exit_code = call_draft(args=['version'])
    if exit_code != 0:
        log.critical('draft not installed')
    else:
        _check_go_app_version('draft', output, DRAFT_SUPPORTED_VERSIONS)

    # kubectl

    output, exit_code = execute_system_command(['kubectl', 'version', '--client'])
    if exit_code != 0:
        log.critical('kubectl not installed')
    else:
        _check_go_app_version('kubectl', output, KUBECTL_SUPPORTED_VERSIONS)

    # helm

    output, exit_code = execute_system_command(['helm', 'version', '--client'])
    if exit_code != 0:
        log.critical('helm not installed')
    else:
        _check_go_app_version('helm', output, HELM_SUPPORTED_VERSIONS)

    # docker

    output, exit_code = execute_system_command(['docker', 'version'])
    if exit_code != 0:
        log.critical('docker not installed')
    else:
        regex = r" Version:\s+([0-9\.\-a-z]+)"

        matches = re.findall(regex, output)

        if len(matches) != 2:
            raise RuntimeError('parsing docker version failed!')

        supported_versions = DOCKER_SUPPORTED_VERSIONS
        installed_client_version = matches[0]
        installed_server_version = matches[1]

        if installed_client_version in supported_versions:
            log.info('docker client verified successfully')
        else:
            log.warning('docker client installed version ({installed}) was not tested, supported versions: {supported}'
                        .format(
                                installed=installed_client_version,
                                supported=supported_versions
                        )
                        )

        if installed_server_version in supported_versions:
            log.info('docker server verified successfully')
        else:
            log.warning('docker server installed version ({installed}) was not tested, supported versions: {supported}'
                        .format(
                                installed=installed_server_version,
                                supported=supported_versions
                        )
                        )
