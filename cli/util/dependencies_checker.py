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

from collections import namedtuple
from distutils.version import LooseVersion
import re

from draft.cmd import call_draft
from util.system import execute_system_command
from util.logger import initialize_logger


log = initialize_logger(__name__)

DRAFT_MIN_VERSION = LooseVersion('v0.13.0')
KUBECTL_MIN_VERSION = LooseVersion('v1.10')
DOCKER_MIN_VERSION = LooseVersion('18.03.0-ce')
HELM_VERSION = LooseVersion('v2.8.1')


class InvalidDependencyError(Exception):
    pass


"""
namedtuple for holding binary dependency specification.
expected_version: expected dependency version
version_command: function that will be executed to obtain version info
version_command_args: arguments that will be passed to called version_command
version_field: name of field from which version will be parsed (e.g. GitVersion)
match_exact_version: if True, only versions that exactly match expected version should be accepted,
                     if False all versions that are greater or equal to the expected version should be accepted
"""
DependencySpec = namedtuple('DependencySpec', ['expected_version', 'version_command',
                                               'version_command_args', 'version_field',
                                               'match_exact_version'])

DEPENDENCY_MAP = {'draft': DependencySpec(expected_version=DRAFT_MIN_VERSION,
                                          version_command=call_draft,
                                          version_command_args=['version'], version_field='SemVer',
                                          match_exact_version=False),
                  'kubectl': DependencySpec(expected_version=KUBECTL_MIN_VERSION,
                                            version_command=execute_system_command,
                                            version_command_args=['kubectl', 'version', '--client'],
                                            version_field='GitVersion',
                                            match_exact_version=False),
                  'helm client': DependencySpec(expected_version=HELM_VERSION,
                                                version_command=execute_system_command,
                                                version_command_args=['helm', 'version', '--client'],
                                                version_field='SemVer',
                                                match_exact_version=True),
                  'helm server': DependencySpec(expected_version=HELM_VERSION,
                                                version_command=execute_system_command,
                                                version_command_args=['helm', 'version', '--server'],
                                                version_field='SemVer',
                                                match_exact_version=True),
                  'docker client': DependencySpec(expected_version=DOCKER_MIN_VERSION,
                                                  version_command=execute_system_command,
                                                  version_command_args=['docker', 'version',
                                                                        '-f', '{{.Client.Version}}'],
                                                  version_field=None, match_exact_version=False),
                  'docker server': DependencySpec(expected_version=DOCKER_MIN_VERSION,
                                                  version_command=execute_system_command,
                                                  version_command_args=['docker', 'version',
                                                                        '-f', '{{.Server.Version}}'],
                                                  version_field=None, match_exact_version=False),
                  }


def _is_version_valid(installed_version: LooseVersion, expected_version: LooseVersion,
                      match_exact_version=False) -> bool:
    return installed_version == expected_version if match_exact_version else installed_version >= expected_version


def _parse_installed_version(version_output: str, version_field='SemVer') -> LooseVersion:
    regex = r"{version_field}:\"([\w.]+)\"".format(version_field=version_field)
    matches = re.findall(regex, version_output)

    if len(matches) != 1:
        raise ValueError(f'Failed to parse version({version_field}) '
                         f'from following input: {version_output}')

    installed_version = LooseVersion(matches[0])

    return installed_version


def check_dependency(dependency_spec: DependencySpec) -> (bool, LooseVersion):
    """
    Check if dependency defined by given DependencySpec is valid
    :param dependency_spec: specification of dependency to check
    :return: a tuple of validation status and installed version
    """
    output, exit_code = dependency_spec.version_command(dependency_spec.version_command_args)
    if exit_code != 0:
        raise RuntimeError(f'Failed to run {dependency_spec.version_command}'
                           f' with args {dependency_spec.version_command_args}. Output: {output}')

    if dependency_spec.version_field:
        installed_version = _parse_installed_version(output, version_field=dependency_spec.version_field)
    else:
        installed_version = LooseVersion(output.strip())

    return _is_version_valid(installed_version=installed_version, expected_version=dependency_spec.expected_version,
                             match_exact_version=dependency_spec.match_exact_version), installed_version


def check_all_binary_dependencies():
    """
    Check versions for all dependencies of carbon CLI. In case of version validation failure,
     an InvalidDependencyError is raised.
    """
    for dependency_name, dependency_spec in DEPENDENCY_MAP.items():
        try:
            valid, installed_version = check_dependency(dependency_spec)
            if not valid:
                raise InvalidDependencyError(f'{dependency_name} installed version: {installed_version}, does not match'
                                             f' expected version: {dependency_spec.expected_version}')
        except RuntimeError as e:
            error_msg = f'Failed to check {dependency_name} version.'
            log.exception(error_msg)
            raise InvalidDependencyError(error_msg) from e
        except (ValueError, TypeError) as e:
            error_msg = f'Failed to parse {dependency_name} version.'
            log.exception(error_msg)
            raise InvalidDependencyError(error_msg) from e
