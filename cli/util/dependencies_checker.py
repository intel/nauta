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
from util.system import execute_system_command, get_os_version
from util.logger import initialize_logger
from util.exceptions import InvalidDependencyError, InvalidOsError
from cli_text_consts import UTIL_DEPENDENCIES_CHECKER_TEXTS as TEXTS


log = initialize_logger(__name__)

UBUNTU_MIN_VERSION = LooseVersion('16')
WINDOWS_MIN_VERSION = LooseVersion('10')
MACOS_MIN_VERSION = LooseVersion('10.13')

DRAFT_MIN_VERSION = LooseVersion('v0.13.0')
KUBECTL_MIN_VERSION = LooseVersion('v1.10')
KUBECTL_SERVER_MIN_VERSION = LooseVersion('v1.10')
DOCKER_MIN_VERSION = LooseVersion('18.03.0-ce')
HELM_VERSION = LooseVersion('v2.9.1')
HELM_SERVER_CONNECTION_TIMEOUT = 30
NAMESPACE_PLACEHOLDER = '<namespace>'

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
                                          version_command_args=['version', '--tiller-namespace', NAMESPACE_PLACEHOLDER],
                                          version_field='SemVer',
                                          match_exact_version=False),
                  'kubectl': DependencySpec(expected_version=KUBECTL_MIN_VERSION,
                                            version_command=execute_system_command,
                                            version_command_args=['kubectl', 'version', '--client'],
                                            version_field='GitVersion',
                                            match_exact_version=False),
                  'kubectl server': DependencySpec(expected_version=KUBECTL_SERVER_MIN_VERSION,
                                                   version_command=execute_system_command,
                                                   version_command_args=['kubectl', 'version', '--short'],
                                                   version_field='Server Version',
                                                   match_exact_version=False),
                  'helm client': DependencySpec(expected_version=HELM_VERSION,
                                                version_command=execute_system_command,
                                                version_command_args=['helm', 'version', '--client'],
                                                version_field='SemVer',
                                                match_exact_version=True),
                  'helm server': DependencySpec(expected_version=HELM_VERSION,
                                                version_command=execute_system_command,
                                                version_command_args=['helm', 'version', '--server', '--debug',
                                                                      '--tiller-connection-timeout',
                                                                      f'{HELM_SERVER_CONNECTION_TIMEOUT}',
                                                                      '--tiller-namespace', NAMESPACE_PLACEHOLDER],
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

SUPPORTED_OS_MAP = {'ubuntu': UBUNTU_MIN_VERSION,
                    'macos': MACOS_MIN_VERSION,
                    'windows_pro': WINDOWS_MIN_VERSION,
                    'windows_enterprise': WINDOWS_MIN_VERSION}


def _is_version_valid(installed_version: LooseVersion, expected_version: LooseVersion,
                      match_exact_version=False) -> bool:
    return installed_version == expected_version if match_exact_version else installed_version >= expected_version


def _parse_installed_version(version_output: str, version_field='SemVer') -> LooseVersion:
    regex = r"{version_field}:(?:\"([\w.-]+)\"| ([\w.-]+)$)".format(version_field=version_field)
    matches = re.findall(regex, version_output)

    if len(matches) != 1:
        raise ValueError(TEXTS["parse_fail_error_msg"]
                         .format(version_field=version_field, version_output=version_output))

    installed_version = LooseVersion(matches[0][0] or matches[0][1])

    return installed_version


def check_os():
    """ Check if user's OS is supported by dlsctl. """
    try:
        os_name, os_version = get_os_version()
        if os_name == "":
            raise InvalidOsError(TEXTS["unknown_os_error_msg"])
    except InvalidOsError:
        raise
    except Exception as exe:
        raise InvalidOsError(TEXTS["get_os_version_error_msg"]) from exe
    log.info(f"Detected OS: {os_name} {os_version}")
    if os_name not in SUPPORTED_OS_MAP:
        raise InvalidOsError(TEXTS["unsupported_os_error_msg"].format(os_name=os_name, os_version=os_version))
    if not _is_version_valid(os_version, SUPPORTED_OS_MAP[os_name]):
        raise InvalidOsError(TEXTS["invalid_os_version_error_msg"].format(os_name=os_name, os_version=os_version))


def check_dependency(dependency_spec: DependencySpec, namespace: str = None) -> (bool, LooseVersion):
    """
    Check if dependency defined by given DependencySpec is valid
    :param dependency_spec: specification of dependency to check
    :param namespace: k8s namespace where server component of checked dependency is located
    :return: a tuple of validation status and installed version
    """

    if namespace:
        for i, arg in enumerate(dependency_spec.version_command_args):
            dependency_spec.version_command_args[i] = arg.replace(NAMESPACE_PLACEHOLDER, namespace)
    try:
        output, exit_code = dependency_spec.version_command(dependency_spec.version_command_args)
        if exit_code != 0:
            raise RuntimeError
    except RuntimeError as e:
        raise RuntimeError(
            TEXTS["version_cmd_fail_msg"].format(
                version_cmd=dependency_spec.version_command, version_cmd_args=dependency_spec.version_command_args,
                output=output
            )
        ) from e

    if dependency_spec.version_field:
        installed_version = _parse_installed_version(output, version_field=dependency_spec.version_field)
    else:
        installed_version = LooseVersion(output.strip())

    return _is_version_valid(installed_version=installed_version, expected_version=dependency_spec.expected_version,
                             match_exact_version=dependency_spec.match_exact_version), installed_version


def check_all_binary_dependencies(namespace: str):
    """
    Check versions for all dependencies of carbon CLI. In case of version validation failure,
     an InvalidDependencyError is raised.
    :param namespace: k8s namespace where server components of checked dependencies are located
    """
    for dependency_name, dependency_spec in DEPENDENCY_MAP.items():
        try:
            supported_versions_sign = '==' if dependency_spec.match_exact_version else '>='
            valid, installed_version = check_dependency(dependency_spec, namespace=namespace)
            log.info(f'Checking version of {dependency_name}. '
                     f'Installed version: ({installed_version}). '
                     f'Supported version {supported_versions_sign} {dependency_spec.expected_version}.')
            if not valid:
                raise InvalidDependencyError(
                    TEXTS["invalid_dependency_error_msg"].format(
                        dependency_name=dependency_name, installed_version=installed_version,
                        expected_version=dependency_spec.expected_version
                    )
                )
        except FileNotFoundError as e:
            error_msg = TEXTS["dependency_not_installed_error_msg"].format(dependency_name=dependency_name)
            log.exception(error_msg)
            raise InvalidDependencyError(error_msg) from e
        except (RuntimeError, ValueError, TypeError) as e:
            error_msg = TEXTS["version_get_fail_msg"].format(dependency_name=dependency_name)
            log.exception(error_msg)
            raise InvalidDependencyError(error_msg) from e
